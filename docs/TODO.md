# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.2)

- **[MG-14] Let the pre-commit hook write the file rows, so nobody runs floor --write by hand** (opened 2026-11-02) [QUEUED]
  - Done means: when a commit touches production code in a repo that has rules.json, the
    shared pre-commit hook runs health.py floor --write and stages docs/health/files.json and
    floor.json, so a shrink, a new file or a gone file never reaches the ratchet unrecorded. A
    worse floor still refuses, with the confession row, since widening stays the owner's call.
    (Tech: the pre-commit in the setup repo; floor --write exits 1 on a worse floor, which
    refuses the commit; the two files are added to the index after a successful write. In the
    rulebook repo itself the same hook rewrites MANIFEST.sha256 and stages it, since the rows
    it just wrote would otherwise leave the fingerprint list stale on every such commit.)
  - Verify: in a scratch repo on the rulebook, a commit that shrinks a file lands with the
    updated rows staged and the ratchet green right after; a commit that widens a row is
    refused with the row to paste; Check.ps1 green here.
- **[MG-22] Give the comment and style rules a one second scanner** (opened 2026-11-03) [QUEUED]
  - Done means: a session sees a bad comment or a layout slip right after writing it, instead
    of seven minutes later when the full gate goes red. One Python script under tools applies
    the text rules the comment and style tests hold and prints file, line and rule, exit 1 on
    any hit. The shared setup runs it after every edit of a .cs, .py or .ps1 file in a repo on
    the rulebook. (Tech: tools/style_scan.py; a colon, dash or tell in a production comment,
    ticket ids and review talk in any comment, a first summary sentence over 110, comment
    lines over 100 past the style.json count, Python layout, C# double blanks, em dashes in
    the ledger; a PostToolUse hook in the shared settings.json through style_scan.sh; the C#
    tests stay the verdict.)
  - Verify: the script run on this repo prints nothing and exits 0; a planted colon comment in
    Logging prints its file and line and exits 1; the same edit through the hook puts the line
    in front of the session; a full scan of this repo finishes in under a second.
- **[MG-23] Make every count freezing refusal name its baseline and the command that moves it** (opened 2026-11-03) [QUEUED]
  - Done means: when a test that freezes a count goes red, its message says which file holds
    the number and how to move it, so the fix and the baseline land in one edit instead of
    three reruns. The README lists the same in one table. (Tech: the comment budget, silent
    catch, doc width and comment width tests; files.json moved by health.py floor --write,
    style.json hand written under docs/health, warnings.json written by the gate and raised
    by hand with a card.)
  - Verify: each named test's failure text carries its baseline path and command, pinned by
    a test that reads the message builders; the README table lists every baseline the
    rulebook freezes; Check.ps1 green.
- **[MG-17] Let a repo opt its Python into the health and comment rules** (opened 2026-11-03) [QUEUED]
  - Done means: a mod written in Python can be held to the same rules as a C# mod, with the
    200 line gate, the comment budget, the silent catch and long function counts and the
    duplication ratchet reading its listed Python folders, tools/lib included. A repo that
    lists none sees no change. A repo whose record holds zero rows is no longer refused for
    that alone. The day a folder is first listed is its line in the sand, so a file already
    over a line that day is debt, not a refusal. (Tech: rules.json pythonProd, a list of
    folders; health.py and FileRows read .py under them, keyed by repo relative path; the
    comment contract scans them recursively; this repo opts in its own tools folder.)
  - Verify: this repo's rows gain its tools Python; a planted silent except in a listed folder
    is refused by the ratchet; selftest cases cover a Python function over 60 code lines, a
    silent except and the folder day one rule; Offensive Chemist's tree measured from here
    reports rows for every file under its tools; Check.ps1 green.

## Backlog

- [MG-18] 2026-11-03: Decide whether the ledger may let Now go empty, since the owner finds the
  refusal at every last exit annoying and the reason behind it is not written down anywhere; the
  rule has been in the ledger test since its first day (Living Weapons f338eb84, 2026-07-05) and
  reads as a forcing function, so each exit also names what comes next. (Tech: the NotEmpty
  assertion in TodoContractTests and the "Now never goes empty" line in the global CLAUDE.md; a
  change here lands in every repo on the rulebook at its next subtree pull.)
- [MG-5] 2026-11-02: Let the style contract's em dash ban take a per-repo scope list, since data
  files hold design notes with em dashes that are not game text.
- [MG-6] 2026-11-02: Have the shared setup's /gates status print the rulebook version a repo is
  on, so one screen shows both the session gates and the build gates.

## Walled (blocked by engine / external)

- Nothing yet.

## Format (enforced by TodoContractTests)

- Sections, in this order and no others: Now (with the release name in the header), Backlog,
  Walled, Format.
- Now: at most 5 entries. Entry first line: `- **[MG-<n>] <title>** (opened YYYY-MM-DD) [STATUS]`
  where STATUS is QUEUED, BUILDING, AWAITING-LIVE, or BLOCKED(reason). Every entry carries a
  `- Done means:` and a `- Verify:` sub-bullet. Promote from Backlog by filling those in; if Now
  is at cap, demote something first.
- Backlog: entry first line `- [MG-<n>] YYYY-MM-DD: <one sentence>`; indented continuation lines
  are free. Capture new items here in the session they surface.
- ELI5-first prose: the first sentence of every entry, and the opening of every Done means /
  Verify, is plain language a non-programmer follows. Technical detail comes AFTER, in
  continuation lines or a "(Tech: ...)" tail, never instead of it.
- IDs are unique across this file and docs/CHANGELOG.md; never reuse a retired ID.
- Items exit ONLY by moving to docs/CHANGELOG.md when they ship or die: in the shipping commit
  itself, or in the immediately following commit when the exit row cites that commit's own hash.
- No em dashes and no double-dash separators anywhere in this file or the changelog.
- AWAITING-LIVE resolutions (flipping a row out of AWAITING-LIVE) are owner-only.
