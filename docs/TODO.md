# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.2)

- **[MG-18] Let Now go empty** (opened 2026-11-03) [QUEUED]
  - Done means: shipping the last card in Now no longer fails the ledger test, so the owner is
    not made to invent a next card at every last exit. The owner ruled so on 2026-11-03 after
    the reason behind the refusal turned out to be written nowhere. The cap of five and every
    other rule stay. (Tech: the NotEmpty assertion in TodoContractTests goes, and so does the
    "Now never goes empty" sentence in the global CLAUDE.md; every repo on the rulebook takes
    the change at its next subtree pull.)
  - Verify: a scratch ledger with an empty Now passes the ledger test; this repo's own test run
    is green; the global CLAUDE.md no longer carries the sentence.
- **[MG-5] Let the em dash ban take a per-repo scope list** (opened 2026-11-02) [QUEUED]
  - Done means: a repo can name the folders and files where an em dash is banned, so the ban
    reaches its code and docs without reaching data files whose design notes are not game
    text. A repo that lists nothing is not scanned, by the owner's ruling of 2026-11-03. This
    repo lists its own folders. (Tech: rules.json emDashScope, a list of paths; a new style
    contract test walks them and names each line; the README key table gains the row.)
  - Verify: a planted em dash in a listed folder fails the test with its file and line; one in
    an unlisted folder passes; Check.ps1 green here with the scope set.
- **[MG-6] Show the rulebook version on the /gates screen** (opened 2026-11-02) [QUEUED]
  - Done means: one screen shows both the session gates and the build gates, with the rulebook
    version a repo is on, where its build gates run, and whether the pre-commit rows step and
    the style scan hook are live there. (Tech: a rulebook row in the shared setup's gates.py,
    read from gates/VERSION in a mod or VERSION in the rulebook repo, plus the SessionStart
    brief line; tests in test_gates.py.)
  - Verify: /gates in a mod on the rulebook names its version; in a repo off the rulebook the
    row says so; the brief line at session start carries the version; test_gates.py green.

## Backlog

- [MG-24] 2026-11-03: Move the four mods onto rulebook v0.2.0 and fill their rows in the README's
  Who is on it table, with Offensive Chemist opting its tools Python into the health gate on the
  way, so every mod runs the same rules again. (Tech: git subtree pull at v0.2.0 in each mod;
  Offensive Chemist adds pythonProd to its rules.json and Invoke-HealthGate to its pipeline.)

## Walled (blocked by engine / external)

- Nothing yet.

## Format (enforced by TodoContractTests)

- Sections, in this order and no others: Now (with the release name in the header), Backlog,
  Walled, Format.
- Now: at most 5 entries, and it may stand empty between cards. Entry first line:
  `- **[MG-<n>] <title>** (opened YYYY-MM-DD) [STATUS]`
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
