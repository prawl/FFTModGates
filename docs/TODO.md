# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, the same system as the mods with the MG id prefix. "Now" holds what is actively
being worked for the current release (hard cap 5, each entry carries Done means + Verify).
"Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this file only
through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The release ship
gate lives in docs/RELEASE_SCOPE.md.

## Now (release: 0.3)

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
- [MG-32] 2026-11-12: Ten facts in the shared list read proven though nobody has seen them
  on today's game build, only on an older one, while the list's own rule says such facts come in
  uncertain; Patrick decides whether they drop to uncertain or stand. (Tech: PROVEN rows whose
  every live source says "on a build before 1.5.2", against docs/GAME_FACTS.md merge rule 5:
  hiding-all-enemies-wins-battle, resurrect-despawned-unit, spawn-ai-unit-donor-duplication,
  unit-on-unpathable-tile-stranded, render-z-cosmetic-and-hit-restamp,
  world-z-downward-floor-clamped, zero-value-command-ai-silent,
  attack-row-catalog-offset-redirect, float-hover-is-world-z and anim-request-register.
  hide-reveal-ghost-statue was the eleventh, dropped to UNCERTAIN on Patrick's word.)
- [MG-33] 2026-11-12: Battle Brain's own notes carry mistakes the shared fact list has fixed,
  and Battle Brain's session must fix them in its own files, since the keeper never edits
  another repo; Patrick passes the list on. Owed so far: the journal names the chocobo and its
  rider the wrong way round, and its byte table says an end of turn request is wiped clean when
  the game keeps the move's numbers in it. (Tech: FFTBattleBrain docs/SPIKE_FACTS.md lines 1561
  to 1567, rider 0x80 and mount 0x40 per [unit-mount-byte-0x1b4]; line 296, the EndTurn column
  of the byte correlation table, per [endturn-carried-move-bytes].)
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
- [MG-34] 2026-11-12: Check whether a unit's turn really opens on a wiped request, since eight
  recorded turn openings arrived still holding numbers from before. Parked by Patrick until
  the seven clashes of 2026-11-12 are done. (Tech: [request-buffer-reused-across-turns] says
  only the coordinates are zeroed; 8 first calls of a turn on BB's tapes arrived as type 2
  with nonzero bytes at +4, e.g. exam_two_battle_one_unwatched_auto_battle#104.)

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
