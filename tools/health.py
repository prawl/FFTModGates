#!/usr/bin/env python
"""
Code health report, written once per release so the trend builds itself.

Each release gets one record, docs/health/vX.Y.Z.json, holding a snapshot of the production code at
that release and what changed during the cycle since the previous release. docs/HEALTH.md is rebuilt
from those records every time, so never edit it by hand.

What it measures:
  * Snapshot: production and test size, test-to-production ratio, comment share, silent (empty)
    catches, methods over 60 code lines, production files over 200 code lines, and duplicated
    8-line blocks.
  * Cycle: commits that touched production code, how many read like a repair (called fix-shaped, the
    subject starts with Stop, Fix, Restore, Correct, Guard, Re-anchor... or says bug, crash, wrong,
    no longer), hotspots (cycle commits times branch points), and fix rate per domain folder.
    Commits touching more than 8 production files count as sweeps and are left out of fix counts.
    Renames are followed, so a file moved into a folder keeps its history.

How it runs, so nobody has to remember it:
  * The repo's Publish.ps1 calls `report --write` after a package passes verification, which writes
    the record for the version being packaged. In GitHub Actions it runs on tag pushes only and also
    writes the run's step summary.
  * The shared gate functions (gates/pipeline/gates.ps1) call `status` on every build. It stays
    quiet while a version is in development and prints a warning box when a tagged release has no
    record, or when a record is written but not committed.
  * The same gate calls `ratchet` on every build: the working tree's snapshot against the best
    committed record. Silent catches, long methods, long files and repeated code may not rise, and
    the test ratio may not fall; a build that makes one of them worse is refused, the same as a red
    test. A row the newest record does not hold yet is not judged until a release writes it. The
    bar is read from the last commit, never from the working copy, and `--base` adds a second ref
    (the main branch, or the commit a push started from) so an edit to the memory cannot lower it.
    A repo with no committed memory is refused until its first floor is committed.
  * `floor` snapshots the working tree between releases, so an improvement holds from the day it
    lands. A floor only moves the good way.

Where things are comes from rules.json at the repo root (prod, tests, modConfig, devDefine,
healthDir, healthMd). The repo root is the first folder above this script that holds a .git entry,
or the one named with --repo.

Usage:
  python gates/tools/health.py report --version 2.4.0 --write     # write the record and rebuild HEALTH.md
  python gates/tools/health.py report --version 2.4.0             # print the section, write nothing
  python gates/tools/health.py report --version 2.3.4 --ref v2.3.4 --write   # backfill an old release
  python gates/tools/health.py status [--committed] [--strict]    # the reminder; --strict exits 1
  python gates/tools/health.py ratchet                            # exit 1 when the working tree is worse than the best record
  python gates/tools/health.py floor --write                      # record today's numbers as the floor
  python gates/tools/health.py --selftest
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import subprocess
import time
import sys
import tarfile

RULES_FILE = "rules.json"
# The selftest's folder names. A real run replaces every one of these from rules.json in configure().
REPO = None
PROD = "Prod/"
TESTS = "Tests/"
HEALTH_MD = "docs/HEALTH.md"
HEALTH_DIR = "docs/health"
MOD_CONFIG = "mod/ModConfig.json"
DEV_DEFINE = None
SCRIPT = "tools/health.py"
SWEEP = 8
LONG_METHOD = 60
# The owner's refactor trigger for a production file. Test files are exempt.
LONG_FILE = 200
DUP_WINDOW = 8

FIX = re.compile(
    r"^(Stop|Fix|Correct|Restore|Guard|Prevent|Re-anchor|Repair|Revert|Undo)\b"
    r"|\b(fix(es|ed)?|bug|crash\w*|regress\w*|broken|wrong|hotfix|no longer)\b"
    r"|^Keep .*\b(from|instead|honest|alive|working|watching|painting|inside|when|after|across|through)\b", re.I)
BRANCH = re.compile(r"\b(if|for|foreach|while|case|catch)\b|&&|\|\|")
EMPTY_CATCH = re.compile(r"catch(\s*\([^)]*\))?(\s*when\s*\([^)]*\))?\s*\{\s*(/\*[^*]*\*/)?\s*\}")
CATCH = re.compile(r"\bcatch\b")
MODS = r"(?:public|internal|private|protected|static|override|virtual|sealed|async|unsafe|extern|new|partial)"
METHOD = re.compile(r"^\s*(?:%s\s+)+(?:[\w<>\[\],?. ]+\s+)?(\w+)\s*\([^;]*$" % MODS)


def find_repo(start):
    """The first folder at or above start that holds a .git entry, a folder or a worktree file."""
    here = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            raise RuntimeError("no .git found above %s; pass --repo" % start)
        here = parent


def configure(repo):
    """Point every folder name at the repo's rules.json. Keys left out keep the defaults above."""
    global REPO, PROD, TESTS, HEALTH_MD, HEALTH_DIR, MOD_CONFIG, DEV_DEFINE, SCRIPT
    REPO = os.path.abspath(repo)
    SCRIPT = os.path.relpath(os.path.abspath(__file__), REPO).replace(os.sep, "/")
    path = os.path.join(REPO, RULES_FILE)
    if not os.path.isfile(path):
        raise RuntimeError("%s has no %s" % (REPO, RULES_FILE))
    with open(path, encoding="utf-8-sig") as h:
        rules = json.load(h)
    for key in ("prod", "tests"):
        if key not in rules:
            raise RuntimeError("%s lacks the %s key" % (RULES_FILE, key))
    PROD = rules["prod"].rstrip("/") + "/"
    TESTS = rules["tests"].rstrip("/") + "/"
    HEALTH_MD = rules.get("healthMd", HEALTH_MD)
    HEALTH_DIR = rules.get("healthDir", HEALTH_DIR)
    MOD_CONFIG = rules.get("modConfig", MOD_CONFIG)
    DEV_DEFINE = rules.get("devDefine")


def git(*args, check=True):
    out = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if check and out.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), out.stderr.decode("utf-8", "replace").strip()))
    return out.stdout.decode("utf-8", "replace")


def vkey(tag):
    """(2, 3, 4) for v2.3.4 or 2.3.4; None for anything that is not a release version."""
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", tag.strip())
    return tuple(int(x) for x in m.groups()) if m else None


def release_tags():
    return sorted((t for t in git("tag", "-l", "v*").split() if vkey(t)), key=vkey)


def pick_previous(version, tags, is_ancestor):
    """The newest release tag older than version that is an ancestor of the report's ref."""
    want = vkey(version)
    older = [t for t in tags if vkey(t) < want]
    for t in reversed(older):
        if is_ancestor(t):
            return t
    return None


def read_tree(ref):
    """Every production and test .cs file at ref, as {path: text}."""
    raw = subprocess.run(["git", "-C", REPO, "archive", ref, PROD.rstrip("/"), TESTS.rstrip("/")],
                         capture_output=True)
    if raw.returncode != 0:
        raise RuntimeError("git archive %s failed: %s" % (ref, raw.stderr.decode("utf-8", "replace")))
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw.stdout), mode="r:") as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(".cs"):
                files[member.name] = tar.extractfile(member).read().decode("utf-8-sig", "replace")
    return files


def is_comment(line):
    return line.strip().startswith(("//", "/*", "*"))


def code_lines(text):
    return [l for l in text.split("\n") if l.strip() and not is_comment(l)]


def branch_points(text):
    return len(BRANCH.findall("\n".join(code_lines(text))))


def method_lengths(text):
    """Code-line length of each method and constructor body, by brace matching."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = METHOD.match(lines[i])
        if not m or "=>" in lines[i] or is_comment(lines[i]):
            i += 1
            continue
        depth, started, j = 0, False, i
        while j < len(lines):
            bare = re.sub(r'"(?:\\.|[^"\\])*"|//.*', "", lines[j])
            for ch in bare:
                if ch == "{":
                    depth += 1
                    started = True
                elif ch == "}":
                    depth -= 1
            if started and depth <= 0:
                break
            if not started and bare.strip().endswith(";"):
                break
            j += 1
        if started:
            out.append((m.group(1), len(code_lines("\n".join(lines[i:j + 1])))))
            i = j + 1
        else:
            i += 1
    return out


def duplicated_share(texts):
    """Share of code lines sitting inside an 8-line block that appears more than once."""
    windows = collections.defaultdict(list)
    norm = {}
    for path, text in texts.items():
        rows = [re.sub(r"\s+", " ", l).strip() for l in code_lines(text)]
        rows = [r for r in rows if len(r) > 3 and not r.startswith(("using ", "{", "}"))]
        norm[path] = rows
        for k in range(len(rows) - DUP_WINDOW + 1):
            windows[tuple(rows[k:k + DUP_WINDOW])].append((path, k))
    dup = set()
    for spots in windows.values():
        if len(spots) > 1:
            for path, k in spots:
                dup.update((path, k + t) for t in range(DUP_WINDOW))
    total = sum(len(r) for r in norm.values())
    return (len(dup) / total) if total else 0.0


def domain_of(path):
    parts = path[len(PROD):].split("/")
    return parts[0] if len(parts) > 1 else "(root)"


def dev_only(text):
    """True for a file wrapped whole in the repo's dev define, since it compiles out of release builds."""
    if not DEV_DEFINE:
        return False
    first = next((l.strip() for l in text.split("\n") if l.strip()), "")
    return first.startswith("#if " + DEV_DEFINE)


def snapshot(files):
    prod = {p: t for p, t in files.items() if p.startswith(PROD)}
    tests = {p: t for p, t in files.items() if p.startswith(TESTS)}
    prod_lines = sum(len(t.split("\n")) for t in prod.values())
    test_lines = sum(len(t.split("\n")) for t in tests.values())
    comments = sum(sum(1 for l in t.split("\n") if is_comment(l)) for t in prod.values())
    methods = [n for t in prod.values() for _, n in method_lengths(t)]
    return {
        "prod_files": len(prod),
        "prod_lines": prod_lines,
        "code_lines": sum(len(code_lines(t)) for t in prod.values()),
        "test_files": len(tests),
        "test_lines": test_lines,
        "test_ratio": round(test_lines / prod_lines, 2) if prod_lines else 0,
        "comment_share": round(comments / prod_lines, 3) if prod_lines else 0,
        "empty_catches": sum(len(EMPTY_CATCH.findall(t)) for t in prod.values()),
        "catches": sum(len(CATCH.findall(t)) for t in prod.values()),
        "methods": len(methods),
        "long_methods": sum(1 for n in methods if n > LONG_METHOD),
        "long_files": sum(1 for t in prod.values() if len(code_lines(t)) > LONG_FILE),
        "duplication": round(duplicated_share(prod), 4),
    }


def cycle(since, ref, prod_files):
    """Commits in since..ref, credited to each production file under its name at ref."""
    rng = "%s..%s" % (since, ref) if since else ref
    raw = git("log", rng, "--no-merges", "-M", "--name-status", "--format=@@%H\t%s")
    alias = {f: f for f in prod_files}
    per = collections.defaultdict(lambda: [0, 0])
    total = prod_commits = fix_commits = 0
    for block in raw.split("@@")[1:]:
        lines = block.strip("\n").split("\n")
        subject = lines[0].split("\t", 1)[1] if "\t" in lines[0] else ""
        touched = set()
        for row in lines[1:]:
            parts = row.split("\t")
            if len(parts) < 2:
                continue
            if parts[0].startswith("R") and len(parts) >= 3:
                cur = alias.get(parts[2])
                if cur:
                    alias[parts[1]] = cur
            else:
                cur = alias.get(parts[-1])
            if cur:
                touched.add(cur)
        total += 1
        if not touched:
            continue
        prod_commits += 1
        is_fix = len(touched) <= SWEEP and bool(FIX.search(subject))
        fix_commits += is_fix
        for f in touched:
            per[f][0] += 1
            per[f][1] += is_fix
    return total, prod_commits, fix_commits, per


def build_record(version, ref):
    tags = release_tags()
    since = pick_previous(version, tags, lambda t: subprocess.run(
        ["git", "-C", REPO, "merge-base", "--is-ancestor", t, ref], capture_output=True).returncode == 0)
    files = read_tree(ref)
    prod = {p: t for p, t in files.items() if p.startswith(PROD)}
    total, prod_commits, fix_commits, per = cycle(since, ref, set(prod))
    # Dev spikes compile out of release builds, so they never rank as hotspots. Ties break on the
    # path so a record rebuilt later comes out the same.
    hot = sorted(((p, c, fx, branch_points(prod[p]), len(code_lines(prod[p])))
                  for p, (c, fx) in per.items() if not dev_only(prod[p])),
                 key=lambda r: (-r[1] * max(r[3], 1), r[0]))
    domains = collections.defaultdict(lambda: [0, 0, 0, 0])
    for p, text in prod.items():
        d = domains[domain_of(p)]
        d[0] += 1
        d[1] += len(code_lines(text))
        c, fx = per.get(p, (0, 0))
        d[2] += c
        d[3] += fx
    date = git("log", "-1", "--format=%cs", ref).strip()
    return {
        "version": version.lstrip("v"),
        "ref": ref,
        "sha": git("rev-parse", "--short=8", ref + "^{commit}").strip(),
        "date": date,
        "since": since,
        "snapshot": snapshot(files),
        "cycle": {
            "commits": total,
            "prod_commits": prod_commits,
            "fix_commits": fix_commits,
            "fix_share": round(fix_commits / prod_commits, 3) if prod_commits else 0,
        },
        "hotspots": [{"file": p[len(PROD):], "commits": c, "fixes": fx, "branches": b, "code": n}
                     for p, c, fx, b, n in hot[:10]],
        "domains": [{"domain": k, "files": v[0], "code": v[1], "changes": v[2], "fixes": v[3]}
                    for k, v in sorted(domains.items(), key=lambda kv: (-kv[1][2], kv[0]))],
    }


def read_at(ref, relpath):
    """A file's text at a git ref, or None when the ref or the file is not there."""
    out = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (ref, relpath)], capture_output=True)
    return out.stdout.decode("utf-8-sig", "replace") if out.returncode == 0 else None


def load_records(ref=None):
    """Release records from the working tree, or from a git ref so an uncommitted edit cannot move the bar."""
    recs = []
    if ref is None:
        folder = os.path.join(REPO, HEALTH_DIR)
        if os.path.isdir(folder):
            for name in os.listdir(folder):
                if name.endswith(".json") and vkey(name[:-5]):
                    with open(os.path.join(folder, name), encoding="utf-8") as h:
                        recs.append(json.load(h))
    else:
        for path in git("ls-tree", "--name-only", ref, HEALTH_DIR + "/", check=False).split():
            name = os.path.basename(path)
            if name.endswith(".json") and vkey(name[:-5]):
                text = read_at(ref, path)
                if text:
                    recs.append(json.loads(text))
    return sorted(recs, key=lambda r: vkey(r["version"]), reverse=True)


def pct(x, digits=0):
    return ("%." + str(digits) + "f%%") % (100 * x)


def num(x):
    return "{:,}".format(x)


def change(now, before, fmt, better_low):
    if before is None:
        return ""
    diff = now - before
    if fmt(abs(diff)) == fmt(0):
        return "same"
    arrow = "up" if diff > 0 else "down"
    if better_low is None:
        return "%s %s" % (arrow, fmt(abs(diff)))
    good = (diff < 0) == better_low
    return "%s %s%s" % (arrow, fmt(abs(diff)), "" if good else " (worse)")


def points(x, digits=0):
    return ("%." + str(digits) + "f pts") % (100 * x)


# label, record key, value format, change format, lower is better (None means neutral)
SNAPSHOT_ROWS = [
    ("Production code lines (not blank, not comment)", "code_lines", num, num, None),
    ("Test lines per production line", "test_ratio", lambda x: "%.2f" % x, lambda x: "%.2f" % x, False),
    ("Comment share", "comment_share", lambda x: pct(x), lambda x: points(x), None),
    ("Silent (empty) catches", "empty_catches", num, num, True),
    ("Methods over %d code lines" % LONG_METHOD, "long_methods", num, num, True),
    ("Production files over %d code lines" % LONG_FILE, "long_files", num, num, True),
    ("Code in repeated 8-line blocks", "duplication", lambda x: pct(x, 1), lambda x: points(x, 1), True),
]

# A patch release of a commit or two says nothing about fix rate, so "last cycle" means the most
# recent earlier release with at least this many production commits.
COMPARABLE_CYCLE = 10


def comparable(records, index):
    for r in records[index + 1:]:
        if r["cycle"]["prod_commits"] >= COMPARABLE_CYCLE:
            return r
    return None


def render_section(rec, prev, cmp=None):
    s, c = rec["snapshot"], rec["cycle"]
    ps = prev["snapshot"] if prev else {}
    out = ["## v%s, %s" % (rec["version"], rec["date"]), ""]
    span = "since %s" % rec["since"] if rec["since"] else "from the first commit"
    lead = ("%s production commit%s %s, %s of them fix-shaped" % (
        num(c["prod_commits"]), "" if c["prod_commits"] == 1 else "s", span, pct(c["fix_share"])))
    if cmp:
        lead += " (%s in v%s)" % (pct(cmp["cycle"]["fix_share"]), cmp["version"])
    top = rec["hotspots"][0]["file"] if rec["hotspots"] else None
    out.append(lead + "." + (" Top hotspot: %s." % top if top else ""))
    out += ["", "| Measure | This release | Change since last |", "| --- | --- | --- |"]
    for label, key, fmt, dfmt, better_low in SNAPSHOT_ROWS:
        # A record older than the measure shows a dash instead of failing the whole page.
        if key not in s:
            out.append("| %s | - |  |" % label)
            continue
        delta = change(s[key], ps.get(key), dfmt, better_low)
        out.append("| %s | %s | %s |" % (label, fmt(s[key]), delta))
    out += ["", "Hotspots this cycle (commits times branch points):", "",
            "| File | Commits | Fix-shaped | Branch points | Code lines |", "| --- | --- | --- | --- | --- |"]
    for h in rec["hotspots"]:
        out.append("| %s | %d | %d | %d | %d |" % (h["file"], h["commits"], h["fixes"], h["branches"], h["code"]))
    out += ["", "Domains this cycle:", "",
            "| Domain | Files | Code lines | Changes | Fix-shaped | Fix rate |", "| --- | --- | --- | --- | --- | --- |"]
    for d in rec["domains"]:
        rate = pct(d["fixes"] / d["changes"]) if d["changes"] else "-"
        out.append("| %s | %d | %s | %d | %d | %s |" % (d["domain"], d["files"], num(d["code"]), d["changes"], d["fixes"], rate))
    out.append("")
    return out


def render_md(records):
    out = ["# Code Health", "",
           "STATUS: CONTRACT (generated by tools/health.py at every release; never edit by hand)", "",
           "Written by tools/health.py once per release (Publish.ps1 runs it) and rebuilt from docs/health/*.json.",
           "Do not edit this file by hand; the next release overwrites it. tools/health.py explains every measure.", "",
           "## Trend", "",
           "| Release | Date | Code lines | Tests per line | Comments | Silent catches | Long methods | Long files | Repeated code | Fix-shaped of commits | Top hotspot |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in records:
        s = r["snapshot"]
        top = r["hotspots"][0]["file"] if r["hotspots"] else "-"
        out.append("| v%s | %s | %s | %.2f | %s | %d | %d | %s | %s | %s | %s |" % (
            r["version"], r["date"], num(s["code_lines"]), s["test_ratio"], pct(s["comment_share"]),
            s["empty_catches"], s["long_methods"], s.get("long_files", "-"), pct(s["duplication"], 1),
            "%s of %d" % (pct(r["cycle"]["fix_share"]), r["cycle"]["prod_commits"]), top))
    out.append("")
    for k, r in enumerate(records):
        out += render_section(r, records[k + 1] if k + 1 < len(records) else None, comparable(records, k))
    return "\n".join(out)


def banner(lines, warn):
    width = max(len(l) for l in lines) + 4
    edge = "!" * width if warn else "=" * width
    return "\n".join([edge] + ["| " + l.ljust(width - 4) + " |" for l in lines] + [edge])


def cmd_report(args):
    version = (args.version or mod_version()).lstrip("v")
    ref = args.ref or "HEAD"
    rec = build_record(version, ref)
    records = [r for r in load_records() if r["version"] != rec["version"]] + [rec]
    records.sort(key=lambda r: vkey(r["version"]), reverse=True)
    k = [r["version"] for r in records].index(rec["version"])
    prev = records[k + 1] if k + 1 < len(records) else None
    cmp = comparable(records, k)
    section = "\n".join(render_section(rec, prev, cmp))
    if args.write:
        os.makedirs(os.path.join(REPO, HEALTH_DIR), exist_ok=True)
        with open(os.path.join(REPO, HEALTH_DIR, "v%s.json" % rec["version"]), "w", encoding="utf-8", newline="\n") as h:
            json.dump(rec, h, indent=1)
            h.write("\n")
        with open(os.path.join(REPO, HEALTH_MD), "w", encoding="utf-8", newline="\n") as h:
            h.write(render_md(records))
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as h:
            h.write("# Code health, v%s\n\n%s\n" % (rec["version"], section))
    s, c = rec["snapshot"], rec["cycle"]
    lines = ["CODE HEALTH v%s (%s, since %s)" % (rec["version"], rec["sha"], rec["since"] or "the start"),
             "%d production commits, %s fix-shaped%s" % (c["prod_commits"], pct(c["fix_share"]),
                 " (%s in v%s)" % (pct(cmp["cycle"]["fix_share"]), cmp["version"]) if cmp else ""),
             "Top hotspot: %s" % (rec["hotspots"][0]["file"] if rec["hotspots"] else "-"),
             "Silent catches %d, long methods %d, long files %d, repeated code %s" % (
                 s["empty_catches"], s["long_methods"], s["long_files"], pct(s["duplication"], 1))]
    if args.write:
        lines.append("Wrote %s and %s/v%s.json. Commit them with the release." % (HEALTH_MD, HEALTH_DIR, rec["version"]))
    print(banner(lines, warn=False))
    if not args.write:
        print("\n" + section)
    return 0


def mod_version():
    """The version being worked on, from the mod's ModConfig.json or a plain file holding only the version."""
    with open(os.path.join(REPO, MOD_CONFIG), encoding="utf-8-sig") as h:
        if MOD_CONFIG.lower().endswith(".json"):
            return json.load(h)["ModVersion"]
        return h.read().strip()


def status_problems(tags, have, uncommitted, first_tracked):
    """What the reminder must say. tags are the release tags, have the versions with a record,
    uncommitted the versions whose record exists but is not committed, and first_tracked the oldest
    version with a record (older tags are history, not debt)."""
    problems = []
    if first_tracked is None:
        return ["No health records yet. Run: python %s report --write" % SCRIPT]
    for t in tags:
        v = t.lstrip("v")
        if vkey(v) >= vkey(first_tracked) and v not in have:
            problems.append("%s was released with no health record. Run: python %s report --version %s --ref %s --write" % (t, SCRIPT, v, t))
    if uncommitted:
        names = ", ".join("v" + v for v in sorted(uncommitted, key=vkey))
        problems.append("Written but not committed: %s. Commit docs/health and docs/HEALTH.md." % names)
    return problems


def cmd_status(args):
    tags = release_tags()
    if args.committed:
        listing = git("ls-tree", "--name-only", "HEAD", HEALTH_DIR + "/", check=False).split()
        have = {os.path.basename(p)[:-5].lstrip("v") for p in listing if p.endswith(".json") and vkey(os.path.basename(p)[:-5])}
        uncommitted = set()
    else:
        have = {r["version"] for r in load_records()}
        dirty = git("status", "--porcelain", "--untracked-files=all", "--", HEALTH_DIR, HEALTH_MD, check=False).splitlines()
        uncommitted = {m.group(1) for l in dirty for m in [re.search(r"v(\d+\.\d+\.\d+)\.json", l)] if m}
    first = min(have, key=vkey) if have else None
    problems = status_problems(tags, have, uncommitted, first)
    if problems:
        print(banner(["CODE HEALTH REMINDER"] + problems, warn=True))
        if os.environ.get("GITHUB_ACTIONS"):
            for p in problems:
                print("::warning title=Code health::%s" % p)
        return 1 if args.strict else 0
    latest = max(have, key=vkey)
    print("  -> Code health: last record v%s. The next one is written when Publish.ps1 packages v%s." % (latest, mod_version()))
    return 0


# The ratchet rows: record key, label, lower is better.
RATCHET_ROWS = [
    ("empty_catches", "silent (empty) catches", True),
    ("long_methods", "methods over %d code lines" % LONG_METHOD, True),
    ("long_files", "production files over %d code lines" % LONG_FILE, True),
    ("duplication", "code in repeated 8-line blocks", True),
    ("test_ratio", "test lines per production line", False),
]


def worktree_files():
    """Every production and test .cs file in the working tree, keyed like read_tree, build output skipped."""
    files = {}
    for top in (PROD, TESTS):
        for folder, dirs, names in os.walk(os.path.join(REPO, top.rstrip("/"))):
            dirs[:] = [d for d in dirs if d not in ("bin", "obj")]
            for name in names:
                if name.endswith(".cs"):
                    path = os.path.join(folder, name)
                    key = os.path.relpath(path, REPO).replace(os.sep, "/")
                    with open(path, encoding="utf-8-sig", errors="replace") as h:
                        files[key] = h.read()
    return files


FLOOR_FILE = "floor.json"


def load_floor(ref=None):
    """The floor record from the working tree, or from a git ref; None when absent."""
    if ref is None:
        path = os.path.join(REPO, HEALTH_DIR, FLOOR_FILE)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as h:
            return json.load(h)
    text = read_at(ref, HEALTH_DIR + "/" + FLOOR_FILE)
    return json.loads(text) if text else None


def best_base(records, floor):
    """Per ratchet row, the best value any committed record holds and which record holds it. floor may be one record or a list."""
    floors = floor if isinstance(floor, list) else ([floor] if floor else [])
    base, origin = {}, {}
    for key, label, better_low in RATCHET_ROWS:
        for rec in list(records) + floors:
            v = rec["snapshot"].get(key)
            if v is None:
                continue
            name = "v" + rec["version"] if "version" in rec else "floor " + rec["sha"] + (" on " + rec["where"] if rec.get("where") else "")
            if key not in base or (v < base[key] if better_low else v > base[key]):
                base[key], origin[key] = v, name
    return base, origin


def ratchet_problems(base, now, origin=None):
    """The rows where now is worse than base, as sentences."""
    out = []
    for key, label, better_low in RATCHET_ROWS:
        b, n = base.get(key), now.get(key)
        # A measure added after the newest record was written has nothing to ratchet against yet.
        # The row stays silent until a release writes a record that holds it.
        if b is None or n is None:
            continue
        worse = n > b if better_low else n < b
        if worse:
            out.append("%s: %s, was %s%s" % (label, n, b, " in %s" % origin[key] if origin and key in origin else ""))
    return out


def ratchet_memory(base_ref):
    """The committed records and floors the ratchet judges against, plus notes on what it could not read."""
    records, floors, notes = load_records("HEAD"), [], []
    head_floor = load_floor("HEAD")
    if head_floor:
        floors.append(head_floor)
    if base_ref:
        base_floor = load_floor(base_ref)
        if base_floor:
            base_floor["where"] = base_ref
            floors.append(base_floor)
            records += load_records(base_ref)
        else:
            notes.append("No floor readable at %s; judging against HEAD only." % base_ref)
    if not records and not floors:
        working = load_floor()
        if working:
            floors.append(working)
            notes.append("The floor is not committed yet; commit %s/%s with this change." % (HEALTH_DIR, FLOOR_FILE))
    return records, floors, notes


def cmd_ratchet(args):
    records, floors, notes = ratchet_memory(args.base)
    for note in notes:
        print("  -> " + note)
    if not records and not floors:
        print(banner(["CODE HEALTH RATCHET REFUSED: no committed record to judge against",
                      "Run: python %s floor --write, then commit it with this change." % SCRIPT], warn=True))
        return 1
    base, origin = best_base(records, floors)
    problems = ratchet_problems(base, snapshot(worktree_files()), origin)
    against = ", ".join(sorted(set(origin.values())))
    if problems:
        print(banner(["CODE HEALTH RATCHET: worse than the best committed value"] + problems
                     + ["Fix the code, or write a new record on purpose and say why in the commit."], warn=True))
        return 1
    print("  -> Code health ratchet: no measure worse than the best committed value (%s)." % against)
    return 0


def floor_rows(rec):
    rows = ["CODE HEALTH FLOOR at %s%s" % (rec["sha"], " (dirty tree)" if rec["dirty"] else "")]
    return rows + ["%s: %s" % (label, rec["snapshot"].get(key)) for key, label, _ in RATCHET_ROWS]


def floor_regressions(now, best, origin):
    """The rows a new floor would set worse than the best on record; a floor only moves the good way."""
    return ratchet_problems(best, now, origin)


def cmd_floor(args):
    """Snapshot the working tree as the floor record, so today's numbers hold until a release record betters them."""
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout.strip() != ""
    rec = {"sha": sha, "date": time.strftime("%Y-%m-%d"), "dirty": dirty, "snapshot": snapshot(worktree_files())}
    rows = floor_rows(rec)
    best, origin = best_base(load_records("HEAD"), load_floor("HEAD"))
    worse = floor_regressions(rec["snapshot"], best, origin)
    if worse and not args.allow_worse:
        print(banner(["CODE HEALTH FLOOR REFUSED: a floor only moves the good way"] + worse
                     + ["Fix the code, or pass --allow-worse with the owner's say and name it in the commit."], warn=True))
        return 1
    if worse:
        rec["allowed_worse"] = worse
        rows.append("Allowed worse by the owner: " + "; ".join(worse))
    if args.write:
        os.makedirs(os.path.join(REPO, HEALTH_DIR), exist_ok=True)
        path = os.path.join(REPO, HEALTH_DIR, FLOOR_FILE)
        with open(path, "w", encoding="utf-8", newline="\n") as h:
            json.dump(rec, h, indent=1)
            h.write("\n")
        rows.append("Wrote %s/%s. Commit it with the change that earned it." % (HEALTH_DIR, FLOOR_FILE))
    print(banner(rows, warn=False))
    return 0


def selftest():
    cases = []

    def check(name, ok):
        cases.append((name, bool(ok)))

    check("vkey orders releases", sorted(["v2.10.0", "v2.3.4", "v2.3.10"], key=vkey) == ["v2.3.4", "v2.3.10", "v2.10.0"])
    check("vkey refuses a non-release tag", vkey("v2.4.0-beta") is None)
    tags = ["v2.3.3", "v2.3.4", "v2.4.0"]
    check("previous release skips the version itself", pick_previous("2.4.0", tags, lambda t: True) == "v2.3.4")
    check("previous release must be an ancestor", pick_previous("2.4.0", tags, lambda t: t != "v2.3.4") == "v2.3.3")
    check("no previous release before the first", pick_previous("2.3.3", tags, lambda t: True) is None)
    for s in ["Stop a Retry from paying a kill twice", "Fix the twin grant on 1.5.2",
              "Keep new weapons in the bag when a battle is fled or retried",
              "Re-anchor the roster read", "The banner no longer shows a battle late"]:
        check("fix-shaped: " + s, FIX.search(s))
    for s in ["Add a probe for the status engine", "Tick the roster drill box",
              "Move the Grows line up", "Keep the readme current"]:
        check("not fix-shaped: " + s, not FIX.search(s))
    code = "class A {\n  // if this\n  void M() {\n    if (a && b) { x(); }\n    try { y(); } catch (Exception) { }\n  }\n}\n"
    check("branch points skip comments", branch_points(code) == 3)
    check("empty catch found", len(EMPTY_CATCH.findall(code)) == 1)
    check("empty catch with a note found", len(EMPTY_CATCH.findall("catch (Exception) { /* why */ }")) == 1)
    check("a catch with a body is not empty", not EMPTY_CATCH.findall("catch (Exception ex) { Log(ex); }"))
    check("a filtered empty catch is still empty", len(EMPTY_CATCH.findall("catch (Exception ex) when (ex is IOException) { }")) == 1)
    long_body = "  internal void Big()\n  {\n" + "".join("    x%d();\n" % i for i in range(70)) + "  }\n"
    ctor = "  public Engine(int a,\n      int b)\n  {\n    a = b;\n  }\n"
    lens = dict(method_lengths(long_body + ctor))
    check("long method measured", lens.get("Big", 0) > LONG_METHOD)
    check("constructor measured", "Engine" in lens and lens["Engine"] < 10)
    block = "".join("int v%d = %d;\n" % (i, i) for i in range(10))
    big = "".join("int v%d = %d;\n" % (i, i) for i in range(LONG_FILE + 1))
    files = {PROD + "Big.cs": big, PROD + "Exact.cs": big.rsplit("\n", 2)[0], TESTS + "BigTests.cs": big}
    check("a production file over %d code lines is counted" % LONG_FILE, snapshot(files)["long_files"] == 1)
    check("a test file over %d code lines is exempt" % LONG_FILE, snapshot({TESTS + "T.cs": big})["long_files"] == 0)
    check("comments do not make a file long", snapshot({PROD + "A.cs": "// a\n" * 300 + "int a;\n"})["long_files"] == 0)
    check("repeated block found", duplicated_share({"a.cs": block, "b.cs": block}) == 1.0)
    check("unique code not repeated", duplicated_share({"a.cs": block, "b.cs": block.replace("int", "long")}) == 0.0)
    global DEV_DEFINE
    check("nothing is dev only when the repo names no dev define", not dev_only("#if MODDEV\nusing System;\n"))
    DEV_DEFINE = "MODDEV"
    check("a whole-file dev spike is dev only", dev_only("\n#if MODDEV\nusing System;\n"))
    check("a normal file is not dev only", not dev_only("using System;\n#if MODDEV\n"))
    DEV_DEFINE = None
    check("domain of a root file", domain_of(PROD + "Engine.cs") == "(root)")
    check("domain of a folder file", domain_of(PROD + "Kills/KillTracker.cs") == "Kills")
    check("status asks for a first record", status_problems(tags, set(), set(), None))
    check("status quiet when every tracked tag has a record", not status_problems(tags, {"2.3.3", "2.3.4", "2.4.0"}, set(), "2.3.3"))
    check("status flags a released tag with no record", any("v2.4.0" in p for p in status_problems(tags, {"2.3.3", "2.3.4"}, set(), "2.3.3")))
    check("status ignores tags older than the first record", not status_problems(["v1.0.0", "v2.3.4"], {"2.3.4"}, set(), "2.3.4"))
    check("status flags an uncommitted record", any("not committed" in p for p in status_problems(tags, {"2.3.3", "2.3.4", "2.4.0"}, {"2.4.0"}, "2.3.3")))
    rec = {"version": "2.4.0", "date": "2026-10-20", "since": "v2.3.4", "sha": "abc",
           "snapshot": {"code_lines": 100, "test_ratio": 2.0, "comment_share": 0.2, "empty_catches": 4,
                        "long_methods": 1, "long_files": 1, "duplication": 0.01},
           "cycle": {"prod_commits": 10, "fix_commits": 2, "fix_share": 0.2},
           "hotspots": [{"file": "Engine.cs", "commits": 5, "fixes": 1, "branches": 9, "code": 50}],
           "domains": [{"domain": "(root)", "files": 1, "code": 50, "changes": 5, "fixes": 1}]}
    old = json.loads(json.dumps(rec))
    old["version"], old["snapshot"]["empty_catches"] = "2.3.4", 2
    del old["snapshot"]["long_files"]
    md = render_md([rec, old])
    check("trend has a row per release", "| v2.4.0 |" in md and "| v2.3.4 |" in md)
    check("a rise in silent catches reads as worse", "up 2 (worse)" in md)
    check("first release shows no change column", md.count("## v") == 2)
    check("long files render for a record that holds them", "| Production files over %d code lines | 1 |" % LONG_FILE in md)
    check("a record older than the long file measure renders a dash", "| Production files over %d code lines | - |" % LONG_FILE in md)
    best, origin = best_base([rec, old], None)
    check("the ratchet base is the best committed value per row", best["empty_catches"] == 2 and origin["empty_catches"] == "v2.3.4" and best["test_ratio"] == 2.0)
    floor = {"sha": "abc1234", "date": "2026-10-27", "dirty": False, "snapshot": {"empty_catches": 1, "long_methods": 3, "long_files": 0, "duplication": 0.0, "test_ratio": 1.0}}
    best2, origin2 = best_base([rec, old], floor)
    check("a floor record joins the base and wins where it is best", best2["empty_catches"] == 1 and origin2["empty_catches"] == "floor abc1234" and best2["long_methods"] == 1)
    base_floor = dict(floor, sha="b2b2b2b", where="origin/main", snapshot=dict(floor["snapshot"], long_methods=0))
    best3, origin3 = best_base([rec], [floor, base_floor])
    check("a floor on the base ref joins the base too and names where it came from", best3["long_methods"] == 0 and origin3["long_methods"] == "floor b2b2b2b on origin/main")
    check("a rise above the best value names where the best was set", any("in floor abc1234" in p for p in ratchet_problems(best2, dict(best2, empty_catches=2), origin2)))
    check("the floor banner names the commit and every ratchet row", floor_rows(floor)[0] == "CODE HEALTH FLOOR at abc1234" and len(floor_rows(floor)) == 1 + len(RATCHET_ROWS))
    check("a floor that would be worse than the best on record is a regression, a better one is not",
          floor_regressions(dict(best2, empty_catches=3), best2, origin2) and not floor_regressions(dict(best2, empty_catches=0), best2, origin2))
    tiny = json.loads(json.dumps(old))
    tiny["version"], tiny["cycle"]["prod_commits"], tiny["cycle"]["fix_share"] = "2.3.3", 1, 0.0
    check("a tiny patch cycle is skipped for comparison", comparable([rec, tiny, old], 0) is old)
    check("share changes read in points", change(0.24, 0.38, points, None) == "down 14 pts")
    check("a change below display precision reads same", change(0.0080, 0.0083, lambda x: points(x, 1), True) == "same")
    base = {"empty_catches": 2, "long_methods": 1, "long_files": 0, "duplication": 0.01, "test_ratio": 1.5}
    check("ratchet quiet when nothing is worse", not ratchet_problems(base, dict(base, empty_catches=1, test_ratio=1.6)))
    check("ratchet flags a new silent catch", any("silent" in p for p in ratchet_problems(base, dict(base, empty_catches=3))))
    check("ratchet flags a falling test ratio", any("test lines" in p for p in ratchet_problems(base, dict(base, test_ratio=1.4))))
    check("ratchet flags more repeated code", any("repeated" in p for p in ratchet_problems(base, dict(base, duplication=0.02))))
    check("ratchet flags a new long file", any("files over" in p for p in ratchet_problems(base, dict(base, long_files=1))))
    older = {k: v for k, v in base.items() if k != "long_files"}
    check("ratchet skips a row the base record does not hold", not ratchet_problems(older, dict(base, long_files=5)))
    passed = sum(ok for _, ok in cases)
    for name, ok in cases:
        if not ok:
            print("FAIL: " + name)
    print("health selftest: %d/%d passed." % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main():
    if "--selftest" in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser(description="Per-release code health report.")
    ap.add_argument("--repo", help="the repo root, default the first folder above this script with a .git entry")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("report")
    rp.add_argument("--version", help="release version, default mod/ModConfig.json ModVersion")
    rp.add_argument("--ref", help="commit or tag to measure, default HEAD")
    rp.add_argument("--write", action="store_true", help="write the record and rebuild docs/HEALTH.md")
    rp.add_argument("--summary", help="also append the section to this markdown file (GitHub step summary)")
    sp = sub.add_parser("status")
    sp.add_argument("--committed", action="store_true", help="judge the committed tree, not the working tree")
    sp.add_argument("--strict", action="store_true", help="exit 1 when there is something to remind about")
    rt = sub.add_parser("ratchet")
    rt.add_argument("--base", help="a second ref whose memory also sets the bar, such as origin/main or the commit a push started from")
    fp = sub.add_parser("floor")
    fp.add_argument("--write", action="store_true")
    fp.add_argument("--allow-worse", dest="allow_worse", action="store_true", help="the owner's say that a worse floor is wanted; name it in the commit")
    args = ap.parse_args()
    configure(args.repo or find_repo(os.path.dirname(os.path.abspath(__file__))))
    if args.cmd == "report":
        return cmd_report(args)
    if args.cmd == "floor":
        return cmd_floor(args)
    if args.cmd == "ratchet":
        return cmd_ratchet(args)
    try:
        return cmd_status(args)
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        # The reminder must never stop a build; say why it could not look and move on.
        print("  -> Code health reminder could not run: %s" % exc)
        return 0


if __name__ == "__main__":
    sys.exit(main())
