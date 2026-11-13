# Changelog (work-ledger exits)

STATUS: CONTRACT (machine-checked by TodoContractTests)

Where docs/TODO.md items land when they ship, die, or retract; newest first within a cycle.
Entry first line: `- [MG-<n>] SHIPPED <hash> YYYY-MM-DD: <summary>`, or WONTFIX / RETRACTED
with a date and no hash.

## 0.3 cycle

- [MG-46] SHIPPED efe7fc3 2026-11-13: The game's AI thinks in a dry run where nothing rolls,
  so when its trial meets Blade Grasp or Arrow Guard it takes the cut hit chance of 100 less
  Brave as it stands, and every reaction a trial hit raises counts as firing. This corrects
  MG-44's "roll Brave for a miss": the outcome there holds, a Brave 100 grasper reads 0 percent,
  but no roll happens. The mode global is also set by more than the hit preview. Read from the
  exe on disk, nothing written to the game. (Tech: [ai-trial-runs-blade-grasp-check] and
  [effect-code-picks-hit-reactions]; BattleRoutine 0x14031F130 sets 0x14186AF80 to 1 at
  0x14031F23C and back to 0 at 0x14031F2FF around 0x14031f534 and 0x140320920, which reach the
  trial; the queue helpers 0x14030bdc0, 0x14030be18, 0x14030be68 and 0x14030beb4 skip the roll
  while it is not 0; other writers 0x14030d1cc, 0x14030f030 and 0x14030fe60.)

- [MG-45] SHIPPED ca29df5 2026-11-13: Every flag in the game's AI table now has a name, so the
  model and the simulator can say what kind of move each one is to the AI: whom it aims at,
  whether it can be reflected, whether it checks the target's turn timing, and the rest. Each
  of the 27 names the mod loader knows matched one bit on all 512 abilities. (Tech:
  [ability-ai-flag-names]; the simulator's four unported flag kinds are TargetMap, Reflectable,
  CheckCT_Target and most likely RandomHits.)

- [MG-44] SHIPPED 3b68458 2026-11-13: The game's AI never tests a target's reactions itself.
  It meets them only in its trial run of each candidate act, which goes through the same hit
  code a real act does: Blade Grasp and Arrow Guard cut the hit chance to 100 less Brave and
  roll Brave for a miss, so at 100 Brave the trial always misses, as the old write ups say.
  The same code picks which reaction a hit would raise, Counter among them, and what the AI
  scores from that is not read yet. Read from the exe on disk, nothing written to the game.
  (Tech: [ai-trial-runs-blade-grasp-check] and [effect-code-picks-hit-reactions]; FUN_14038ABA4
  to 0x140281ce8, 0x1403099b0 and 0x14030afec; 0x14030a488 from 0x14038a665 and 0x14038ace0;
  the roll 0x140278e68; mode global 0x14186AF80, set to 2 only by the hit preview 0x140283c00.)

- [MG-43] SHIPPED 3b68458 2026-11-13: On Patrick's call the poison count goes to 0 when poison
  ends, as 118 of 120 recorded endings show. The other 2 were a poison bit written in from
  outside during a test, which the game cleared after one tick while the count stayed at 36.
  The old Living Weapons row from before 1.5 stays, marked superseded. (Tech: new
  [poison-bit-and-count]; [poison-bit-and-timer] CONTRADICTED; the odd two at
  probe_20261106_024920.jsonl#152 and #154.)

- [MG-39] SHIPPED efa3498 2026-11-13: Every battle input on the simulator's list of what the
  game's AI reads now has a row saying where it lives in memory, all still uncertain. Elements
  and immunities come straight from the job table the game keeps in its exe, and timed status
  counts, MP, reactions, charging and the mount bytes sit where the rows say across 133
  recordings. MP, level and experience, and a ride ending, wait on Patrick's sign-off with video
  frames. Five inputs need acting in the game (MG-40) and two clashes need his call (MG-42).
  Worked from recordings, plus read only reads of three tables in the running game, with
  nothing written to it. (Tech: new [job-table-row-layout] at 0x140785E30,
  [unit-immune-statuses-from-job], [charged-move-mp-paid-on-landing],
  [timed-status-count-bytes] +0x66 to +0x75, [mount-pair-bytes-clear-together],
  [mount-roles-reversed-in-start-pair], [unit-record-ai-setting-bytes] +0x195 to +0x19A and
  [auto-battle-ai-throws-items]; evidence added to [unit-element-bytes-0x76], [unit-mp-words],
  [unit-record-level-byte], [unit-record-stat-bytes], [unit-reaction-bits-0x94],
  [poison-bit-and-timer], [status-three-layer-bitfields], [unit-record-charge-fields],
  [unit-mount-byte-0x1b4] and [ability-ai-target-flags]; +0x1EF is the lasting inflicted
  layer, not this turn's; the death counter at +0x07 was already proven.)

- [MG-38] SHIPPED cd14a3a 2026-11-13: A fact is now proven only after Patrick signs off on two
  kinds of evidence set out raw for him: a memory read naming the address, the value and what
  in the game changed it, and something seen in the game. Until then the row says awaiting
  sign-off, and the keeper can no longer flip a row alone. (Tech: GAME_FACTS.md rule 6, rule 4
  and the PROVEN mark; no row had used "keeper verified", and the contract test still accepts
  it, MG-41.)

- [MG-37] SHIPPED 5513178 2026-11-12: The row on how a unit's turn opens now says what the
  recordings show: the request slot is reused, and at a turn's open it mostly holds that unit's
  own last request, with one tile number wiped. It is uncertain, resting on memory reads only,
  and the turn opening row merged into it so the list holds one fact. (Tech:
  [request-buffer-reused-across-turns] narrowed on Patrick's call, PROVEN in BB 2026-10-26 noted
  as for the old wording; [turn-open-request-holds-own-last-act] retired into it.)

- [MG-34] SHIPPED 8afcc17 2026-11-12: A unit's turn does not open on a wiped request. The
  request mostly holds that unit's own last Act, its facing and its last target, with only one
  tile number wiped, so the old proven row that says otherwise goes to Patrick as MG-37. Worked
  offline from recordings only, nothing read from or written to the game. (Tech:
  [turn-open-request-holds-own-last-act], UNCERTAIN, since merged into
  [request-buffer-reused-across-turns] by MG-37; 569 first calls of a turn on Battle
  Brain's 22 tapes: +4 to +7 its own last Act 244 of 246, +0x10 and +0x14 its own last request
  403 of 456, +C its own facing 98 of 109, +8 zeroed whenever it changed, 113 all zero.)

- [MG-32] SHIPPED 9b51615 2026-11-12: Ten facts that read proven though they were only ever
  seen on an older game build are settled on Patrick's word. Two stay proven, noting they were
  seen only before 1.5.2, and eight drop to uncertain: four he no longer recalls, and four he
  first kept and the same day was not certain of. (Tech: kept PROVEN with "Patrick agreed
  2026-11-12", citing Living Weapons' BodyDoubleSpike probe that proved both:
  resurrect-despawned-unit and spawn-ai-unit-donor-duplication. Dropped to UNCERTAIN, the old
  yes named in the evidence: hiding-all-enemies-wins-battle, zero-value-command-ai-silent,
  attack-row-catalog-offset-redirect, anim-request-register, then
  unit-on-unpathable-tile-stranded, render-z-cosmetic-and-hit-restamp,
  world-z-downward-floor-clamped and float-hover-is-world-z. The co-tiled lock he raised already
  had its row, co-tiled-units-soft-lock, UNCERTAIN. The recheck of what is left is MG-36.)

- [MG-31] SHIPPED bf22877 2026-11-12: The fact keeper may now mark a fact proven without Patrick
  when one frame of our recorded video shows it and a memory read agrees, never two of one kind,
  each ruling out that the game would have done it anyway and both kept where anyone can check
  them. A fact that cannot be seen on screen still waits for Patrick. (Tech: docs/GAME_FACTS.md
  rule 6 and the PROVEN mark; Tests/GameFactsContractTests.cs takes "keeper verified YYYY-MM-DD"
  only beside a video frame source and a separate memory read source, with three new test rows.)

- [MG-29] SHIPPED 92f6e40 2026-11-12: Every mod now has one shared list of how the game works, 665
  facts, instead of each keeping its own notes. All of Battle Brain's research journal and Living
  Weapons' live ledger and self test plan went in, each fact once, with how sure we are, what showed
  it and which mods lean on it. A reviewer checked 40 random rows against their sources and found 1
  wrong, since fixed. The two earliest chunks were then checked claim by claim, and the details
  missing there were put back. What was left out, line by line, is below: claims about the mods
  rather than the game, and details a row does not carry.
  - Battle Brain journal lines 1 to 589: 62, 338, 360, 373, 379, 383, 385, 387, 410, 416, 421, 443,
    465 and 523 are Battle Brain's own hook, driver, gate, recorder, handshake, hold budget and
    timing; 393 is another mod's startup message; 586 names cases never reached; 448 is a driver's
    plan arriving in time. Details no row carries: 174, which request facing value is which
    direction; 237, a facing write holding on an idle turn; 348, the Move asked 6.2 s later, after
    the animation; 400, the caller addresses holding still through a hold; 480, a tile thickness
    field with no byte given; 558, the unit staying on (3,9).
  - Journal lines 590 to 1138: 1069, a tool's file rename failing on Windows.
  - Journal lines 1139 to 1669: 1237, 1279, 1311, 1326, 1597 and 1626 are Battle Brain's plans, gate
    and log checks. Details no row carries: 1164 to 1166, tile byte 6 bit 0x04 is not a dip marker,
    with dip never defined; 1592 to 1593, a written Poison read back; 1607, a stock Auto-Potion;
    1322, 1509 to 1510 and 1524 to 1526, tool notes.
  - Journal lines 1670 to 2271: 1803, 1870, 1920, 2035, 2077, 2113, 2116 and 2254 are Battle Brain's
    tools and bookkeeping; 2229 is another mod's config. Details no row carries: line 2001's mode
    word 0x140D408F4 and new game byte 0x1407829FA, no meaning given; 1937's tip about selling
    potions; 1814's rule on outside scripts, only its race caveat kept.
  - Journal lines 2272 to 2906: 2322, 2393, 2397, 2434, 2525, 2607, 2630, 2636, 2642 and 2667 are
    the mod's fight file, driver and leave flags; 2617 has too few turns; 2639 is Windows, not the
    game; 2893 is another mod's config; 2500 does not say which action table it means, a question
    still open.
  - Living Weapons ledger to line 1314: 333 [extended-inventory-boot-arm], a mod feature.
  - Ledger lines 1315 to 2335: 1347 [renewal-regen-aura] and 1363 [kill-attribution-low-entropy] are
    mod logic. Details no row carries: 1517 an action counter; 1579 the undead bit never exercised;
    1595 a nameId kept across a job change; 1739 a charged Cure landing about 7 s on; 1771 a clone's
    passive AI and its +0x1BC host slot; 1803 the acting node id dword 0x140CF873C and the hover
    byte 0x140C6CFE0 + id x 9; 1821 a hidden unit displaced one tile; 1851 a +0x1EE ally bit read;
    1867 key 221, the placeholder Toadja; 1967 the placeholder text on Evading, Performing and
    Critical; 1997 the stale static copy 0x140893C00 and a facing rollback at teardown; 2045 the
    slope and flag meanings; 2177 a mirror re-copy; 2187 the ten writers of 0x140D407A0; 2234 the
    statics block flag at 0x1407B0760 + 0x1C; 2310 the picker table set 0x14067FA90.
  - Ledger lines 2336 to 3467: 2470 and 2934 are Living Weapons' painter cache; 2678 and 3199
    already have rows; 3063's retracted part, its standing claim being a row already; 3113 is the
    mod's code disagreeing with itself; 3239 is a limit of a probing method; 3157
    [crit-chance-settable] and 3171 [guest-traitor-flip] carry no date to cite.
  - Self test plan lines 97 to 99, 128 to 130, 132 to 135, 291 to 292, 294 to 295 and 303 to 304:
    tool claims, plans and predictions.
  (Tech: docs/GAME_FACTS.md held by Tests/GameFactsContractTests.cs; 441 journal claims and 178
  ledger entries read in seven chunks, the left out lists adding up per chunk. The two pilot chunks
  kept no list, so every claim there was matched to rows again: 56 of 57 ledger entries by slug, 44
  of 89 journal claims by address, the other 45 judged by hand. A spot check of 10 hand calls found
  6 wrong, so all 45 were judged again under the rule that a dropped detail is fixed or listed: 2
  rows fixed, 2 added, 7 details listed, one since carried. A second spot check of 20, 10 hand calls
  and 10 address matches, found 11 wrong, 2 of the matches pointing at unrelated rows, all fixed.
  The other 34 address matches were then judged by hand: 18 held, and 16 had dropped details, now
  carried on 14 rows, 4 of those having pointed at the wrong row. All 89 journal claims are now
  judged by hand.)

## 0.2 cycle

- [MG-24] SHIPPED 733d72b 2026-11-03: The four mods now run rulebook v0.2.0 and the README table
  says so with each hookup commit. Each took the tag with a subtree pull from the local rulebook
  and got the shared pre-commit shim, so the rows step and the scanner hook are live there; two
  stale attribution guards were kept beside the shim as pre-commit.before. Every shared gate ran
  green on the new rules in all four; Living Weapons needed a second run after one of its own
  tests left an lw_cfg folder behind once, a leak the rulebook did not change. (Tech: git
  subtree pull --prefix gates from the local path at v0.2.0 with --squash; install_git_hooks.sh
  in each; Color Customizer pulled through a scratch worktree and a fast forward around its
  dirty tree.)
- [MG-5] SHIPPED 5a6096f 2026-11-03: A repo can now say where its em dash ban applies, so the
  ban reaches its code and docs without reaching data files whose design notes are not game
  text. A repo that lists nothing is not scanned, by the owner's ruling of 2026-11-03; this
  repo lists its docs, code, tools, pipeline, selftest, README and check script. (Tech:
  rules.json emDashScope, folders or files; a style contract test walks them, skips binaries
  and names each line; the scanner applies the same rule; the README key table gains the row.)
- [MG-25] SHIPPED 5a6096f 2026-11-03: A total or a row the owner widened under a card now stays
  widened after that card ships, instead of the ratchet going red on the next build against
  the main branch. Found the moment MG-17 shipped, when the base ref's old floor came back for
  three totals and the check went red. (Tech: valid_allowances in health.py reads the card
  from TODO.md and CHANGELOG.md at the ref; a selftest case pins that a SHIPPED row is a card.)
- [MG-18] SHIPPED ef3027b 2026-11-03: Shipping the last card in Now no longer fails the ledger
  test, so nobody has to invent a next card at every last exit. The owner ruled so on
  2026-11-03, once the reason behind the refusal turned out to be written nowhere. The cap of
  five and every other rule stay. (Tech: the NotEmpty assertion left TodoContractTests; the
  Format section says Now may stand empty; the global CLAUDE.md dropped its sentence; every
  repo on the rulebook takes the change at its next subtree pull.)
- [MG-6] SHIPPED ef3027b 2026-11-03: One screen now shows both the session gates and the build
  gates. The /gates table has a rulebook row with the version a repo carries, whether the
  pre-commit rows step and the style scan hook are live there, and the scan's last hit; the
  session start line names the version too. Its first live run showed Color Customizer with no
  shared pre-commit shim. (Tech: rulebook_version and rulebook in the shared setup's gates.py,
  reading gates/VERSION in a mod or VERSION in this repo; five tests in test_gates.py.)
- [MG-17] SHIPPED a1de979 2026-11-03: A mod written in Python can now be held to the same rules
  as a C# mod. A repo lists the folders in rules.json and every .py under them, tools/lib
  included, gets a row with the 200 line gate, the comment budget, the silent except and
  long def counts and the duplication ratchet; the comment and style contracts read them
  too. A repo that lists nothing sees no change, and one whose record holds no C# row is no
  longer refused for that alone. Found hooking up Offensive Chemist, whose ten tools files
  now measure from a scratch clone with gate.py as its one debt row. This repo opted in its
  own tools folder and widened three totals under this card, since the day a folder is first
  listed is its line in the sand. (Tech: rules.json pythonProd; health.py prod_root, row_name,
  function_lengths, SILENT_EXCEPT and fresh_folders; FileRows carries a Python flag; the
  docstring first sentence stands in for the summary; eleven selftest cases and three
  theories.)
- [MG-14] SHIPPED 625776e 2026-11-03: Nobody runs floor --write by hand any more. When a commit
  touches production code in a repo on the rulebook, the shared pre-commit writes the health
  file rows and stages them, so a shrink, a new file or a gone file never reaches the ratchet
  unrecorded. A floor that would be worse still refuses the commit with the row to paste. In
  this repo the same hook rewrites the fingerprint list on every commit. (Tech: health_rows.py
  behind health_rows.sh in the shared setup's git_hooks/pre-commit, after the cold read step;
  rows that did not move are put back so no commit carries a floor whose only change is its
  date; six tests through real commits and a stub health.py; the row shows on the /gates
  screen.)
- [MG-23] SHIPPED b6321a6 2026-11-03: When a test that freezes a count goes red, its message
  now says which file holds the number and what moves it, so the fix and the baseline land in
  one edit instead of three reruns. The README lists every frozen baseline in one table. From
  the second handoff feedback in the private mod, where three baselines went red one at a
  time after one patch. (Tech: FileRows.WriteHint and WidenHint name files.json and health.py
  floor --write; StyleContractTests.FreezeHint names style.json as hand written; the comment
  budget, silent catch, doc width and comment width messages carry them, pinned by a test
  that reads the builders.)
- [MG-22] SHIPPED 35e2059 2026-11-03: A session now sees a bad comment or a layout slip right
  after writing it, instead of seven minutes later when the full gate goes red. One Python
  script under tools answers the comment and style rules in a quarter second, on the whole
  repo or on the files named, and the shared setup runs it after every edit of a .cs, .py,
  .ps1 or .md file in a repo on the rulebook. The C# tests stay the verdict. From the first
  handoff feedback in the private mod, where the gate went red five times on rules a reader
  could not see in advance. (Tech: tools/style_scan.py with the rules in style_rules.py; a
  PostToolUse hook in the shared settings.json through style_scan.sh and style_scan_hook.py,
  exit 2 with the hits on stderr; six hook tests through a stub scanner.)
- [MG-21] SHIPPED 2c679b3 2026-11-03: Deleting unique code can no longer make the duplication
  floor refuse a build. The ratchet now holds the number of lines sitting in repeated blocks,
  not their share of all code, so a shrink with no new repeated line passes. Found swapping
  Color Customizer onto the shared logger, where removing five logger files raised the share
  from 3.13% to 3.19% and the owner had to widen under CC-50. (Tech: the snapshot gains
  duplicated_lines and RATCHET_ROWS judges it in place of duplication, which stays in the
  report; a floor without the key is silent on it until floor --write records it, as this
  repo's floor now does; two selftest cases.)

## 0.1 cycle

- [MG-20] SHIPPED 9ec036c 2026-11-03: Two production files with the same name no longer crash
  the image literal checks. Color Customizer has two StoryCharacterRegistry.cs and two
  ModInitializer.cs, and the allow list and pin table checks threw on the second of each. Now a
  name counts as still needing its entry when any file of that name does. (Tech: ToLookup by
  file name instead of ToDictionary in ImageLiteralContractTests; Color Customizer links the
  contract from v0.1.2 and its 182 shared tests pass.)
- [MG-19] SHIPPED 9ec036c 2026-11-03: A mod still paying its warnings down now has the count
  held so it can only fall. Turning the shared warnings as errors switch off arms a ratchet in
  the health gate that counts the build's compiler warnings and holds them to
  docs/health/warnings.json. The first run writes the record, a lower count moves it, and a
  higher count is refused with the confession row. Color Customizer's first run wrote 263 and a
  planted unused variable was refused. (Tech: Invoke-WarningRatchet inside Invoke-HealthGate,
  armed by ModGatesWarningsAsErrors false in the root Directory.Build.targets; a full rebuild of
  every non test project in rules.json, distinct warning lines; the record holds since, warnings
  and an optional card.)
- [MG-7] SHIPPED 17fee2d 2026-11-03: The README now says which mod runs which rulebook version
  since when, with its hookup commit, so anyone can see when the last mod is in and the paydown
  of the recorded debt can begin. Treasure Master is on v0.1.0 and Living Weapons on v0.1.1;
  Offensive Chemist, Color Customizer and the private mod are not yet. (Tech: the Who is on it
  table in README.md; each hookup updates its row in the same session.)
- [MG-16] SHIPPED 51d20d5 2026-11-03: A mod that already had months of release records can
  now take the rulebook without being told its code is worse than its best month. The first
  floor is the line in the sand, and older records feed the trend but never set a bar. Living
  Weapons' first floor was refused against its v2.1.0 record before this. (Tech: floor.json
  carries since, the first floor's date; since_adoption filters records in the ratchet and the
  floor; three new selftest checks.)
- [MG-15] SHIPPED a0b2da8 2026-11-03: Loading the gate script now prints nothing, and the first
  gate names the rulebook version instead, so a mod test that dot-sources its pipeline script
  and reads the output gets its answer and not the banner. Living Weapons has nine such tests.
  (Tech: the Write-Host moved from the body of gates.ps1 into Invoke-ManifestGate; VERSION
  0.1.1; tag v0.1.1 at 51d20d5.)
- [MG-11] SHIPPED 3da7098 2026-11-03: The rulebook now has a version a mod takes by name, v0.1.0,
  so two mods on one tag run the same rules and a change here reaches a mod only when it pulls
  the next tag. Treasure Master took it first and runs green on it locally and in CI, and
  gates/VERSION prints 0.1.0 in its build log. (Tech: tag v0.1.0 on 3da7098, pushed; the README's
  subtree lines name the tag; Treasure Master hookup commit b8287c9, CI run 41582500395.)
- [MG-13] SHIPPED 3a96d67 2026-11-02: A refused gate now ends with the Backlog row to paste, under
  the next free ledger id, naming the rule it wanted to bend and why, so the paper trail of rules
  that got in the way piles up in one place. The owner widens a rule with floor --write
  --allow-worse --card <id>, which must be a row of docs/TODO.md; the floor and files records store
  the card, and the ratchet judges a widened key at HEAD alone so the override survives CI's base
  ref. (Tech: health.py confession, has_card, next_id, valid_allowances, shield, floor_faults;
  Get-Confession in gates.ps1 for the manifest gate.)
- [MG-3] SHIPPED fe4af4c 2026-11-02: Every production file now has its own row of comment lines,
  longest block, code lines, silent catches and long methods in docs/health/files.json, and the
  health ratchet holds the file to it on every build. Comments and the block are frozen, code may
  grow to 200 lines, debt only shrinks, a new or renamed file meets the full rule, partial parts
  count as one file, and a shrunk row must be committed. (Tech: health.py floor --write writes the
  rows, ratchet judges them against HEAD and the base ref, FileRows.cs feeds the comment budget and
  silent catch tests, comments.json and silentCatchAllowlist are gone.)
- [MG-4] SHIPPED eeea715 2026-11-02: The style contract checks the repo's line ending file against
  the shared one, the same way as the style file, so line endings stop being a judgment call. (Tech:
  StyleContractTests, the byte for byte check over .editorconfig and .gitattributes.)
- [MG-2] SHIPPED eeea715 2026-11-02: The five copies of each contract test are one copy each, losing
  no rule and no example. Tests/ holds the ledger, log, image literal, comment budget, comment,
  silent catch, style and health wiring contracts reading rules.json, and the self test proves all
  172 original facts and 299 examples landed in a shared fact, a local one, or a declared new one.
  (Tech: docs/merge/originals.json is the denominator, docs/merge/mapping.json the placement,
  Selftest/Tests/MergeLedgerTests.cs the proof.)
- [MG-8] SHIPPED 6276a6f 2026-11-02: A mod cannot quietly edit its copy of the rulebook. Every file
  has a fingerprint in MANIFEST.sha256, the manifest gate runs first on every build and refuses a
  copy that differs, and this repo's check refuses a stale list. (Tech: tools/manifest.py write and
  verify, Invoke-ManifestGate, CRLF folded before hashing.)
- [MG-9] SHIPPED 6276a6f 2026-11-02: The health ratchet cannot be dodged by deleting or editing its
  memory. The bar is read from the last commit and from a base ref, never the working copy, and a
  repo with no committed memory is refused. (Tech: load_records and load_floor take a git ref,
  ratchet --base, GATES_BASE_SHA from the workflow.)
- [MG-10] SHIPPED 6276a6f 2026-11-02: The self test builds the rulebook the way a real mod does, a
  library holding the logger and a separate test project seeing it through InternalsVisibleTo, and
  the README names every trap the first mod hits. (Tech: Selftest/Mod and Selftest/Tests.)
- [MG-12] SHIPPED 6276a6f 2026-11-02: The build settings say why they force what they force, and the
  README lists every rules.json key with who reads it.
- [MG-1] SHIPPED 304b739 2026-11-02: One rulebook every mod can take, seeded from the best copy of
  each rule. The shared logger, health.py, the gate functions, the build settings and the style
  file live here with no mod's name inside, and the repo checks itself with its own gates.
  (Tech: Logging/ with fault note and error flush hooks, tools/health.py reading rules.json,
  pipeline/gates.ps1, Directory.Build.targets, Selftest/ with 50 tests; 13 of 13 health numbers
  identical on the newest mod's tree.)
