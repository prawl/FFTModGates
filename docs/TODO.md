# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.1)

- **[MG-2] Merge the five copies of each contract test into one, losing no rule and no example** (opened 2026-11-02) [BUILDING]
  - Done means: Tests/ holds one copy of the ledger, log, image literal, comment budget, comment,
    silent catch, style and health wiring contract tests, reading rules.json for what differs per
    repo, and a check in this repo proves every fact name and every example case from the five
    originals landed in a shared fact, a local fact, or a WONTFIX row. (Tech: the fact matrix is
    the denominator, 89 facts; same-name facts reconcile by diffing masked bodies, strictest
    wins, every InlineData case carried.)
  - Verify: the mapping check in Selftest is green and names 89 of 89 placed.

## Backlog

- [MG-11] 2026-11-02: Pin what a mod takes to a tagged version and prove the gates under both
  PowerShells, since local runs use 5.1 and CI used only 7. (Tech: tag v0.1.0 when Treasure
  Master is green, README pulls the tag; CI runs Check.ps1 under shell powershell and pwsh since
  6276a6f.)
- [MG-13] 2026-11-02: When a gate refuses, its message asks for a confession row in the ledger
  saying which rule it wanted to bend and why, and an owner override must cite that row's id. The
  gate stays red either way; the row is the paper trail, and a pile of rows against one rule says
  the rule is wrong. (Tech: refusal text from the manifest gate and the ratchet names the exact
  Backlog row to paste with the repo's prefix; floor --allow-worse takes --card <id> and checks
  the id exists in TODO.md; the floor record stores the card.)
- [MG-3] 2026-11-02: Make every health number a per-file row that can only shrink, so fixing one
  long method and adding another no longer nets to zero. New files have no row and must meet the
  full rule. A file over 200 code lines fails for a new file, and partial class parts count as
  one file so a split without a real seam cannot pass. (Tech: one baseline json per repo with
  comment lines, longest block, code lines, empty catches and long methods per production file;
  zero growth allowance; a shrink must be committed, not just printed; floor.json totals stay as
  the report.)
- [MG-4] 2026-11-02: Make the style contract check the repo's .gitattributes against the shared
  one too, so line endings stop being a judgment call; three of the five mods have none today.
- [MG-5] 2026-11-02: Let the style contract's em dash ban take a per-repo scope list, since data
  files hold design notes with em dashes that are not game text.
- [MG-6] 2026-11-02: Have the shared setup's /gates status print the rulebook version a repo is
  on, so one screen shows both the session gates and the build gates.
- [MG-7] 2026-11-02: Track which mods are on the shared rules, so the paydown can start when all
  five are. Order after this repo: Treasure Master, Living Weapons, Offensive Chemist, Color
  Customizer, and the private mod once its open branch lands. The per-file ratchet (MG-3) lands
  before the first hookup, so no mod migrates twice.

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
