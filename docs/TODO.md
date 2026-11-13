# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.3)

- **[MG-29] One list of game facts for every mod** (opened 2026-11-12) [BUILDING]
  Every mod keeps its own notes on how the game works, so the same fact gets found twice and a
  fact one mod overturned can still mislead another. This builds one shared list here, written
  by one keeper session that merges what the others send.
  - Done means: every game fact in Battle Brain's research journal and in Living Weapons' live
    ledger and self test plan is one row with its mark, evidence and readers, every claim left
    out is named with why, and the shape test is green. (Tech: docs/GAME_FACTS.md, held by
    Tests/GameFactsContractTests.cs; sources FFTBattleBrain docs/SPIKE_FACTS.md and
    FFTLivingWeapons docs/LIVE_LEDGER.md and docs/research/SELF_TEST_PLAN.md.)
  - Verify: Check.ps1 is green, a reviewer checking 40 random rows against their sources finds
    at most one wrong in ten, and the left out lists account for all 441 marked Battle Brain
    claims and all 178 ledger entries.
  State 2026-11-12 20:30: 249 rows merged (pilots, BB lines 590 to 1138, Patrick's ten live
  facts). Readers have finished BB lines 1139 to 2906 and LW 2336 to the end, and their rows
  wait unmerged as out_*.md in a session scratchpad, beside the merge, cite and readers
  scripts; .claude/handoff.md names the folder. LW 1315 to 2335 was still reading. Several updates
  hit the same row (turn-moved-acted-flags, unit-record-psx-block-shifted-eight,
  battle-lost-when-ramza-is-out, unit-record-index-byte) and need merging by hand, and two
  readers used one id for different claims (human-bit-cleared-at-open-menu). Spend so far in
  tokens: pilots 274k and 426k, readers 238k, 256k, 249k, 262k and 302k, file writes about 60k,
  against an estimate of about 1.6M for all nine.

## Backlog

- [MG-26] 2026-11-03: Opt Offensive Chemist's tools Python into the health gate, since its
  pipeline still skips that gate and its tools would go red the day it lists them, with
  thirteen comment lines holding a colon or a dash, one 284 character opening docstring
  sentence and a bare __init__.py. (Tech: pythonProd in its rules.json; Invoke-HealthGate
  inside its Invoke-SharedGates; Write-HealthReport in Publish.ps1 or publishScript emptied;
  CommentBudget, SilentCatch and FileRows linked into its test project; the first floor comes
  from the pre-commit on that commit.)
- [MG-27] 2026-11-03: The session status line says the C# language server is on whenever its
  plugin loaded, even when the server never started or is still loading its solution, so a
  session trusts a tool that is not there yet; the owner called that misleading on 2026-11-03.
  Make the entry follow the live server, loading, on or off, and gone when it dies. (Tech:
  mods/csharp-lsp-proxy/hooks/register.ts writes the status on session.start with no check;
  the proxy knows the server's pid and sees its progress notifications, so it can write a
  state file the hooks module reads; the first symbol call in a session comes back empty
  while the server is still loading, which reads like a failure, so the proxy could also hold
  that first request until the load ends.)
- [MG-28] 2026-11-03: A session can hand off without leaving its feedback entry, since nothing
  in the chain asks for one, so the scheduled review of the feedback file reads gaps; one of
  the first four real handoffs left none. Have the handoff skill say to write the entry and
  the clear script refuse a handoff whose session has no entry at the bottom of the file.
  (Tech: skills/handoff/SKILL.md step 2; handoff_self.sh already refuses a stale, oversized or
  pointerless note, so the entry check sits beside those; match on the session id in the entry
  header, never on the time, since sessions type the time by guess.)

- [MG-30] 2026-11-12: Add the Battle Brain simulator's checklist of every factor it models to
  the game fact list once that checklist is written, so each factor the game has gets a row and
  the ones the simulator skips read NOT MODELED. (Tech: the third source Patrick named on
  2026-11-12; it waits on that checklist.)

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
