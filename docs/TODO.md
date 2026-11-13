# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.3)

- **[MG-43] Settle the poison count clash on Patrick's call** (opened 2026-11-13) [BUILDING]
  - Done means: a new row says the poison count goes to 0 when poison ends, naming the 2 odd
    endings, and the old pre 1.5 row stays, marked superseded. (Tech: [poison-bit-and-count]
    new, [poison-bit-and-timer] CONTRADICTED.)
  - Verify: both rows read so, and .\Check.ps1 is green.
- **[MG-44] Answer whether the game's AI reads a target's reactions** (opened 2026-11-13) [BUILDING]
  - Done means: the fact list says, with code addresses, where the AI's code meets the reaction
    bytes and that no AI routine tests them itself. (Tech: [ai-trial-runs-blade-grasp-check]
    and [effect-code-picks-hit-reactions], from a disassembly of the 1.5.2 no-DRM exe.)
  - Verify: the rows' call path reads the same in a disassembler, and .\Check.ps1 is green.

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
- [MG-33] 2026-11-12: Battle Brain's own notes carry mistakes the shared fact list has fixed,
  and Battle Brain's session must fix them in its own files, since the keeper never edits
  another repo; Patrick passes the list on. Owed so far: the journal names the chocobo and its
  rider the wrong way round, and its byte table says an end of turn request is wiped clean when
  the game keeps the move's numbers in it. The simulator's AI input list also calls the bytes
  at +0x1EF the statuses put on this turn, when they hold every status a unit carries, and says
  nobody knows where elements live, when the job row and the record now show it. (Tech:
  FFTBattleBrain docs/SPIKE_FACTS.md lines 1561 to 1567, rider 0x80 and mount 0x40 per
  [unit-mount-byte-0x1b4], held until MG-42 settles it; line 296, the EndTurn column of the
  byte correlation table, per [endturn-carried-move-bytes]; sim branch
  docs/research/ai_inputs_list_2026-11-13.txt sections D and G, per
  [status-three-layer-bitfields] and [unit-element-bytes-0x76].)
- [MG-35] 2026-11-12: Living Weapons' own ledger carries mistakes the shared fact list has
  fixed, and Living Weapons' session must fix them in its own files, since the keeper never
  edits another repo; Patrick passes the list on. Owed so far: one paragraph still gives the old
  terrain map address and blames the two tile shift on eyeballing, which a later paragraph of
  the same entry takes back; the hide toggle's summary says the unit's picture vanishes, which
  does not hold on today's build; and the status layers entry says the on screen statuses are
  rebuilt every frame, which two of its own live tests overturn. (Tech: FFTLivingWeapons
  docs/LIVE_LEDGER.md line 3097, "TILE SYSTEM SOLVED 2026-07-28", base 0x140D8DCC0 where
  [terrain-grid-record-base] has 0x140D8DCB0; [hide-reveal-ghost-statue] summary "sprite gone",
  per [gate-byte-hide-drops-sprite]; line 2494, composed "rebuilt every frame as inflicted OR
  innate", per [status-three-layer-bitfields].)
- [MG-36] 2026-11-12: Four facts read proven though every sighting behind them is from an
  older game build, before 1.5.2 or before its copy protected release; recheck each on today's
  build and keep or drop its mark. (Tech: PROVEN rows whose live sources all name an older
  build or are dated before 2026-07-27 with none named: resurrect-despawned-unit and
  spawn-ai-unit-donor-duplication, both kept on Patrick's word, proved together by Living
  Weapons' BodyDoubleSpike probe on 2026-07-10 and not re-verified since;
  invisible-status-steers-ai-targeting, 2026-07-22; table-xml-whole-row-writeback,
  2026-07-14, the modloader's own behaviour. ct-scheduler-adopts-band-slot, flipped
  2026-11-12 though both its sightings are from 2026-06-16, went back to UNCERTAIN.)
- [MG-40] 2026-11-13: Some of the AI's inputs can only be confirmed by doing something in the
  game, so they wait for Patrick's go ahead: Golem's party shield, Reflect and Transparent on a
  unit, whether the AI checks the item stock before using an item, enemy AI settings in a story
  battle, and an elemental hit on a weak or absorbing unit. (Tech: the plans are in the MG-39
  report; rows [unit-record-ai-setting-bytes], [auto-battle-ai-throws-items] and
  [unit-element-bytes-0x76]; Reflect is status id 38 and Transparent id 19, and Golem has no
  row yet; none of the five shows on any recording.)
- [MG-41] 2026-11-13: The fact list's contract test still lets a row say "keeper verified",
  though Patrick's rule of 2026-11-13 retired the keeper's solo flip; make it refuse that
  marker. (Tech: the Agreed regex and the keeper verified branch in
  Tests/GameFactsContractTests.cs; the test ships to every repo in the rulebook, so it takes a
  rulebook bump.)
- [MG-42] 2026-11-13: A chocobo and Ramza paired at a battle's start carried the rider and
  mount bits the other way round while the screen drew Ramza riding, so which bit means rider
  is in doubt. Patrick left both rows as they are until a clean ride on a normal setup in the
  map 116 plan settles it; the poison half of this card is settled as MG-43. (Tech:
  [mount-roles-reversed-in-start-pair] against [unit-mount-byte-0x1b4].)

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
