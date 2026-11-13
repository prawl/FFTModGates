# Game facts

STATUS: CONTRACT (one row per fact, held by GameFactsContractTests in every repo on the rulebook)

What FFT: The Ivalice Chronicles really does, in one list every mod reads. Each row is one thing
the game does, how sure we are of it, what showed it, and which mods break if it is wrong. A
mod's own tricks and habits are not game facts, so they stay in that mod's repo.

The newest list is this file on main in FFTModGates. A mod's `gates/docs/GAME_FACTS.md` is the
list as of the rulebook version it took.

## Who writes it

One session writes this file, the fact keeper in FFTModGates. Every other session sends it facts
and never edits the file. A message carries the fact in plain words, the mark it claims, the
evidence, and the repos that lean on it. The keeper merges it under the rules below and commits.

## A row

| Column | What it holds |
|---|---|
| Id | A short kebab case name in brackets, never reused. Cite a fact by it, as `[unit-move-jump-bytes]`. |
| Fact | The claim, plain words first, then the offsets, ids and addresses. One claim per row. |
| Mark | One of the five marks below. |
| Evidence | What showed it. Each source opens with its kind and a colon and ends with the repo and day it came from in brackets, as `(BB, 2026-10-26)`. Sources are split by semicolons. |
| Leaned on by | The repos whose code or plans rest on it, short names from the repo table, comma separated. |

A cell never holds a pipe character, and a source never holds a semicolon of its own.

## The five marks

- PROVEN: a session saw it hold in the running game, and Patrick agreed. The evidence carries a
  live source and either "Patrick agreed YYYY-MM-DD" or, for a mark brought in from a repo whose
  proven mark was already his call, "proven in BB YYYY-MM-DD" or "proven in LW YYYY-MM-DD".
- UNCERTAIN: read off a tape, a table, the code or someone else's work, or seen live without
  Patrick's agreement yet. Fine to build on with care, but not settled.
- CONTRADICTED: the claim as written does not hold on this build, or the evidence points both
  ways. The evidence says what overturned it. Probe before building on it.
- WALLED: looked into and blocked. Do not retry without new information.
- NOT MODELED: a factor the game has that a tool meant to account for it, today the Battle Brain
  simulator, does not model yet. The row records the gap, not a truth.

## Evidence kinds

| Kind | What it is | Cite as |
|---|---|---|
| live tape | A recorded live session, read during or after it | the tape file and `#<seq>` |
| live watch | Seen in the running game, with or without a log | the log file, or "no log" |
| game table | A table read from the game's data files or from memory | the table and where it lives |
| Ghidra read | The exe's code read on disk, in Ghidra or any disassembler | the function or RVA |
| exe scan | A byte pattern or a file image probe run on the exe without launching it | the pattern or the probe |
| harness run | An automated battle run | the run, the battle and `#<seq>` |
| source read | Someone else's code or notes, not run here | the project and file |
| PSX doc | The FFHacktics wiki or another write up of the PSX game, not checked on this build | the page |

## Builds

An address or offset holds for the build its evidence names. With no build named it is the 1.5.2
no-DRM build (exe sha256 937233f7fe76182a..., image stamp 0x6A5E4A1B). Addresses are preferred
addresses (image base 0x140000000) or RVAs, as their source wrote them.

## How a fact gets merged

1. One claim per row. A claim with a game half and a tool half is split, and the tool half stays
   in its repo.
2. The same fact from two places is one row carrying both sources.
3. A later look that overturns a row marks it CONTRADICTED and says what overturned it. The row
   stays, and its id is never reused.
4. The keeper flips a row to PROVEN once a session saw it hold live and Patrick agreed, and writes
   the day he agreed. Nobody hands the flip back to him.
5. A mark brought in from a repo keeps its word only when it meets this list's rules. A layout
   fact proven only on an older build comes in UNCERTAIN with its old proof named. A script's
   SELF PROVEN comes in UNCERTAIN, cited as a harness run.

## Repos

| Short | Repo |
|---|---|
| BB | FFTBattleBrain, the battle AI mod |
| sim | The Battle Brain simulator, tools/sim in FFTBattleBrain |
| LW | FFTLivingWeapons |
| TM | FFTTreasureMaster |
| OC | FFTOffensiveChemist |
| CC | FFTColorCustomizer |
| GJ | FFTGenericJobs |
| HF | FFTHandsFree |
| MP | FFTMultiplayer |

## Sources

| Source | What is in it | State |
|---|---|---|
| BB docs/SPIKE_FACTS.md | 441 marked claims in 63 sections | being merged |
| LW docs/LIVE_LEDGER.md | 178 entries | being merged |
| LW docs/research/SELF_TEST_PLAN.md | its Appendix A audit of the ledger's marks, and a few game claims | being merged |
| BB sim factor checklist | every factor the simulator models | not written yet |

## Facts

### The AI decision call

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [battle-routine-entry] | The game asks what a computer run unit does next through one routine, BattleRoutine(unit index, action request), returning a 64 bit code, at RVA 0x31F130. | PROVEN | exe scan: MSVC form pattern, one hit at RVA 0x31F130 (BB, 2026-10-26); live watch: hooked there, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, fftivc.together hooked there in step 0 (BB, 2026-10-26); source read: dicene/fftivc.together Mod.cs (BB, 2026-10-26); source read: skeewirt/fftivc-symbol-map, the WotL symbol _Z13BattleRoutineiP13ActionRequest (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-unit-index-is-slot] | The routine's first argument is the acting unit's slot in the battle unit array. | PROVEN | live watch: acting.ptr equals actor_ptr on every call, seq 7 to 12, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-return-two-reasks] | Returning 2 from the routine means not decided yet. The game asks again once a frame, about every 16.6 ms, keeps running, and leaves the request buffer as it was. Returning 0 means decided, and the request in the buffer runs as written. | PROVEN | live watch: 189 asks over 3.2 s with the buffer identical on all 189, seq 56 to 248, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, step 0, edited and unedited requests ran after fftivc.together's hold (BB, 2026-10-26); live watch: a move to (6,7) written into a held request walked there, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); source read: dicene/fftivc.together Mod.cs (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-covers-every-ai-turn] | The same routine decides enemy turns, a player unit on the game's Auto-Battle, and a player unit whose human bit was cleared from outside. | PROVEN | live watch: seq 14 to 24 of probe_20261026_212759.jsonl and session probe_20261026_214658 (BB, 2026-10-26); live watch: no log, the owner's Archer and Knight, cleared at entry, went through it from their first turn in the third battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-prologue-no-rip-operand] | The routine's opening 26 bytes do not depend on where they sit in memory: the first instruction that does, a cmp [rip+x], sil, starts at byte 26. The opening is 48 89 5C 24 08 48 89 74 24 10 48 89 7C 24 18 41 57 48 83 EC 20 33 F6 48 63 F9. | UNCERTAIN | exe scan: the body at RVA 0x31F130 on 1.5.2 no-DRM (BB, 2026-10-26) | BB |
| [battle-routine-direct-call-site] | The routine has one direct caller in .text, a call (E8) at RVA 0x20ADC6, and no jump thunk in .text leads to it. Indirect calls and other sections were not scanned, and the caller has not been seen live. | UNCERTAIN | exe scan: rel32 E8 and E9 scan of .text (BB, 2026-10-26) | BB |
| [battle-routine-runs-on-game-thread] | The game calls the routine on a thread of its own, neither the mod loader's thread nor the first thread started. Which loop drives that thread is not known. | PROVEN | live watch: thread 60412 against loader thread 60112 and first started thread 58132, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-one-call-per-phase] | The game calls the routine once for each phase of a turn and does not ask again when the answer comes at once. An enemy turn with no target in range is one Move request, then one EndTurn request about 1.5 to 2.3 s later, after the walk. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [stock-routine-decides-under-a-millisecond] | The game's own routine decides in well under a millisecond, about 0.26 ms for a Move and 0.002 ms for an EndTurn. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-hold-no-time-limit] | The game sets no time limit on a not decided answer. It kept asking once a frame through holds of 70 s (4,205 asks) and 78.6 s (4,725 asks), ran the released decision normally, and its current action globals held still throughout. | PROVEN | live watch: a 70 s hold on slot 4, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); live tape: first_live_battle_hold_fold_and_handbrake#4735 (BB, 2026-10-27); proven in BB 2026-10-26 | BB |
| [com-command-mode-routine] | A routine at RVA 0x202F34 runs when the game puts a unit into computer command mode, Battle_Set_ComCommandMode in fftivc.together. Its return type is unknown, and the double together declares is suspect. | UNCERTAIN | source read: dicene/fftivc.together (BB, 2026-10-26); exe scan: MSVC form pattern, one hit at RVA 0x202F34 (BB, 2026-10-26) | BB |
| [current-action-byte] | A byte at preferred 0x141872EC4 reads 0 before a unit's Move decision and 255 after it, and stays 255 through the EndTurn request. It sits at spd_back + 0x1824, spd_back being RVA 0x18716A0, and fftivc.together calls it CurrentAction. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); exe scan: the spd_back lea, one hit at RVA 0x316844 resolving to RVA 0x18716A0 (BB, 2026-10-26); source read: dicene/fftivc.together (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [current-action-zero-forces-new-decision] | Writing 0 to the current action byte before calling the routine again makes the game's own AI decide the turn afresh. | UNCERTAIN | source read: dicene/fftivc.together, which does this before re-running the stock routine (BB, 2026-10-26) | BB |
| [ai-plans-whole-turn-before-move] | The game's own AI plans the whole turn before it moves: its Move request already carries the target tile of the action to follow, X at +0x10 and Y at +0x14. | PROVEN | live watch: Move requests from seq 26 on, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: slot 0's Move carried its Act's target, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); proven in BB 2026-10-26 | BB |

### The action request

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [action-request-move-destination] | A Move request (byte +0 is 0) carries the destination tile's X at +4 and Y at +8, each a u16. | PROVEN | live watch: three walks ended on the requested tile by the unit's grid bytes +0x4F and +0x50, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, step 0, Y edited to 0x0E walked to the edited tile (BB, 2026-10-26); live watch: a written move to (6,7) walked there, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [action-request-facing-byte] | Byte +C of a Move request holds the unit's facing, 0 to 3, and the same value rides into the EndTurn request of a turn that moved first, where writing it sets the facing the unit ends its turn with. | PROVEN | live watch: the step 0 edit and the seq 29 overwrite, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [action-request-type-byte] | The action request is 24 bytes, and byte +0 names what it asks for: 0 Move, 1 Act, 2 EndTurn. | PROVEN | live watch: every request in probe_20261026_212759.jsonl (BB, 2026-10-26); source read: dicene/fftivc.together ActionRequest.cs for the 24 byte layout (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [act-request-target-tile] | An Act request carries its target tile's X at +0x10 and Y at +0x14, each a u16. Bytes +0x08 to +0x0B read 0 on an Act, so together's Field_8 label for the target does not hold. | PROVEN | live watch: four Acts checked against the victims' grid bytes, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, human enemies' Acts in the second battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [act-request-skillset-and-ability] | An Act request names its skillset in byte +0x05 and its ability in the u16 at +0x06. A basic Attack is skillset 0x01 ability 0, and a Knight's Arts of War showed skillset 0x07 with abilities 0x8A, 0x8B and 0x91. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, the second battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [act-request-plus-0c-word] | The u16 at +0x0C of an Act request is non zero when a humanoid unit attacks (0x1E, 0x25, 0x5A and 0x5B seen) and 0 when a monster does. What it means is open, a score or the damage being the guesses. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, a Knight's and an Archer's attacks in the second battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [act-request-target-slot-byte] | Byte +0x0F of an Act request often holds the target's slot in the unit array when a humanoid unit attacks, but reads 0xFF on monsters' attacks and on some humanoid ones, so the tile at +0x10 and +0x14 is the reliable target. | UNCERTAIN | live watch: seq 27, 41 and 46 of probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: no log, the second battle of 2026-10-26 evening (BB, 2026-10-26) | BB |
| [act-request-unmapped-bytes] | On every Act request seen, byte +0x0E reads 5 and the u16 at +0x16 reads 0xFFFF, while the low byte of +0x04 varies (0x00, 0x03, 0x04, 0x10 and 0x11 seen). What these bytes mean is open. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [move-request-plus6-not-height] | The u16 at +6 of a Move request is not the destination's height, whatever together's label Destination_Elevation says: the game's own moves wrote 0 there on all 223 seen, on four maps whose destinations stand at heights 0 to 8. | PROVEN | live tape: first_driver_battle_stub_then_opus_plays_the_enemy#7 to #49731 (BB, 2026-10-27); live tape: exam_two_battle_one_unwatched_auto_battle#7 to #102 (BB, 2026-10-27); live tape: exam_two_battle_two_orbonne_fourth_level_unwatched#7 to #106 (BB, 2026-10-27); live tape: first_live_battle_hold_fold_and_handbrake, 87 moves (BB, 2026-10-27); Patrick agreed 2026-10-28 | BB, sim |
| [move-request-plus6-may-be-level] | The u16 at +6 of a Move request may be the level of the destination tile, 0 for the lower and 1 for the upper. Every stock move seen went to a level 0 tile, so it is not yet told apart from always 0. A stock move onto a raised deck (MAP006, MAP043 or MAP064) would settle it. | UNCERTAIN | live tape: first_driver_battle_stub_then_opus_plays_the_enemy#7 to #49731 and three more tapes, 223 stock moves all to level 0 tiles (BB, 2026-10-27) | BB, sim |
| [endturn-facing-byte-after-act-first] | After a turn that acted before it moved, byte +C of the EndTurn request is not a facing: it read 36 on both such turns, against 0 to 3 on every turn that moved first. | PROVEN | live tape: first_live_battle_hold_fold_and_handbrake#4775 (BB, 2026-10-27); live tape: first_live_battle_hold_fold_and_handbrake#4883 (BB, 2026-10-27); Patrick agreed 2026-10-28 | BB, sim |
| [request-buffer-reused-across-turns] | The game keeps one request buffer from turn to turn: a turn's first request still holds the previous turn's type (2) and facing, with only the coordinates zeroed. | PROVEN | live watch: probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [move-request-answered-with-endturn] | Answering a Move request with an EndTurn ends the turn there with the unit unmoved, and the unit's next turn opens as normal. | PROVEN | live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#121 (BB, 2026-10-28); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#138 (BB, 2026-10-28); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#308, at the Move after an Act (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB |
| [act-request-answered-with-move] | Answering an Act request with a Move walks the unit, and the game then asks for the Act again, so the act is put off, not dropped. | PROVEN | live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#271 (BB, 2026-10-28); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#273 (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB |
| [move-request-answered-with-act] | Answering a Move request with an Act runs the Act from where the unit stands, and the game then asks for the Move the unit still has. | PROVEN | live watch: no log, slot 2's attack in the second battle of 2026-10-26 evening (BB, 2026-10-26); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#305 and #308 (BB, 2026-10-28); live tape: s1_retry_act_first_follow_up_move_written_as_act#158 and #160 (BB, 2026-10-28); proven in BB 2026-10-26 | BB |
| [act-over-endturn-after-stay] | An Act written over the EndTurn request that follows a stay, a Move to the unit's own tile, runs, and the game then asks for a Move again and the unit walks. A stay does not spend the move. | PROVEN | live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#403, #406 and #407 (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB |
| [second-act-over-follow-up-move] | After a unit has acted, an Act written over its follow-up Move request still plays: the same attack started again and ended with no effect, the unit did not move, and the game asked for EndTurn next. | PROVEN | live tape: s1_retry_act_first_follow_up_move_written_as_act#160 (BB, 2026-10-28); live tape: s1_retry_act_first_follow_up_move_written_as_act#161 (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB |

### The battle unit record

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [unit-move-jump-bytes] | A unit's Move and Jump, gear and movement abilities counted, are bytes +0x42 and +0x43 of its battle unit record. | PROVEN | live tape: gear_battle_four_known_move_and_jump_pairs_at_dial_100.jsonl.gz#10 (BB, 2026-11-01); PSX doc: FFHacktics wiki Battle Stats (BB, 2026-11-01); Patrick agreed 2026-11-01 | BB, sim |
| [unit-human-control-bit] | Bit 0x08 of a unit's Flags2, at +0x05 and mirrored at +0x1EE, means a human picks its actions. Setting it on both bytes from outside opens the player's menu on an enemy, and clearing it hands the turn to the AI. | PROVEN | live tape: live_check_act_first_walks_and_mid_turn_loss_retries_clean#2585 (BB, 2026-10-29); live watch: Unit Control cleared it on both bytes of both player units at battle entry, 0x0B to 0x03 and 0x08 to 0x00, and the AI played them, session probe_20261026_214658 (BB, 2026-10-26); source read: dicene/fftivc.unitcontrol BattleUnits.cs (BB, 2026-10-26); live watch: FFTMultiplayer PuppetHold held a whole enemy team human for a battle on 1.5 (BB, 2026-10-26); Patrick agreed 2026-10-29 | BB, sim, MP |
| [battle-unit-array-location] | The battle units are 21 records of 0x200 bytes in one array at preferred 0x141853CE0, BattleUnits__bwork in fftivc.unitcontrol. | UNCERTAIN | source read: dicene/fftivc.unitcontrol BattleUnits.cs (BB, 2026-10-26); exe scan: unitcontrol's pattern, one hit at RVA 0x30C87C whose lea r15 at 0x30C8A6 resolves to 0x141853CE0 (BB, 2026-10-26); live watch: the acting slot's address in it matched the actor pointer on every call, probe_20261026_212759.jsonl (BB, 2026-10-26) | BB, sim, LW, HF, MP |
| [unit-record-index-byte] | Byte +0x01 of a unit record is the unit's index, and 0xFF there marks an empty slot. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs (BB, 2026-10-26) | BB, sim |
| [unit-record-job-byte] | Byte +0x03 of a unit record is the unit's job id. A Monk read 78. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs (BB, 2026-10-26); live watch: the Monk at slot 4, brain/probe_20261027_011757.jsonl, a log no longer kept (BB, 2026-10-27) | BB, sim, LW, MP |
| [unit-record-level-byte] | Byte +0x29 of a unit record is the unit's level. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, live there on 1.5 (BB, 2026-10-26) | BB, LW, MP |
| [unit-record-original-brave-faith] | Bytes +0x2A and +0x2C of a unit record hold its original Brave and its original Faith. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, live there on 1.5 (BB, 2026-10-26) | BB, LW, MP |
| [unit-record-in-battle-pulse] | Byte +0x2E of a unit record is what FFTMultiplayer calls the in battle pulse, a marker of being in the battle that does not hold steady. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, live there on 1.5 (BB, 2026-10-26) | BB, LW, MP |
| [unit-record-hp-words] | A unit record holds the unit's HP at +0x30 and its max HP at +0x32. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, live there on 1.5 (BB, 2026-10-26) | BB, sim, LW, MP |
| [unit-grid-xy-bytes] | Bytes +0x4F and +0x50 of a unit record are its grid X and Y. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs (BB, 2026-10-26); live watch: after three walks they read the requested tiles, probe_20261026_212759.jsonl (BB, 2026-10-26) | BB, sim, LW, MP |
| [unit-record-psx-block-shifted-eight] | The battle unit record keeps the PSX block from PA to the elevation bit 8 bytes further on: PA, MA, Speed, CT, Move, Jump, X, Y and the elevation bit each sit 8 bytes past their PSX offset, so CT, at 0x39 on PSX, would be at +0x41. Only Move and Jump are proven there, and X and Y fit the walks. | UNCERTAIN | PSX doc: FFHacktics wiki Battle Stats (BB, 2026-11-01); live tape: gear_battle_four_known_move_and_jump_pairs_at_dial_100.jsonl.gz#10, Move and Jump at the shifted offsets (BB, 2026-11-01) | BB, sim, LW |
| [unit-turn-flags-not-psx-shifted] | The PSX turn flags (turn open, moved and acted at 0x186 to 0x188) have no copy at +0x18E to +0x190 or at +0x19C to +0x19E of the battle unit record: those bytes read the same at a turn's first call and after its move on every tape. | UNCERTAIN | live tape: all 16 tapes, read in docs/research/move_jump_bytes_2026-11-01.json (BB, 2026-11-01); PSX doc: FFHacktics wiki Battle Stats (BB, 2026-11-01) | BB |
| [unit-team-bit-0x10] | Bit 0x10 of a unit's Flags2 at +0x05 marks the enemy side. Enemies read it set (Flags2 0x90 or 0x50, human bit clear), and a unit turned to the player's side, by Charm or by a skillset 0x0E Act, loses it and fights for its new side from then on. | PROVEN | live watch: slots 0, 3 and 4, and slot 1 going 0x50 to 0x40 after the Act at seq 41, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: slot 0 going 0x90 to 0x80 when charmed, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); proven in BB 2026-10-26 | BB, sim |
| [unit-team-bits-0x30] | Bits 0x30 of Flags2 at +0x05 together hold the unit's team, and any non zero value there means not the player's team. Only bit 0x10 has been seen set live. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, the section's sources (BB, 2026-10-26) | BB, sim |
| [unit-guest-flags] | A guest unit shows bits 0x09 in Flags1 at +0x06, or bit 0x04 in Flags2 at +0x05. | UNCERTAIN | source read: dicene/fftivc.unitcontrol and FFTMultiplayer MatchState.cs, the section's sources (BB, 2026-10-26) | BB, sim |
| [unit-record-bytes-changing-at-move] | When a unit decides a Move its record changes at +0x41, +0x1B8 and +0x1B9, and after the walk +0x50, +0x1B9 and, on a three tile walk, +0x51 have changed. +0x1B8 and +0x1B9 change at every call, a counter or CT being the guess. | UNCERTAIN | live watch: per slot record diffs, probe_20261026_212759.jsonl (BB, 2026-10-26) | BB |
| [unit-record-bytes-changing-at-act] | When a unit decides an Act its record also changes at +0x1BB, +0x1BE, +0x1C0, +0x1CE, +0x1CF, +0x1E6 and +0x1E7, and a player unit's at +0x34, +0x1EC, +0x1ED, +0x1CA and +0x1E5 as well. | PROVEN | live watch: per slot record diffs, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |

### Battle state

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [battle-mode-byte-turn-sides] | The battle mode byte at preferred 0x1409069A0 reads 3 on the player's turn and 5 on the enemy's, the reading carried over from 1.5. | CONTRADICTED | live watch: it read 3 during enemy turns, probe_20261026_212759.jsonl (BB, 2026-10-26); source read: FFTHandsFree on 1.5 for the old reading (BB, 2026-10-26) | BB, LW, TM, HF, MP |
| [actor-pointer-acting-unit] | A pointer at preferred 0x14186AF68 holds the acting unit's record address, its combat frame, while it decides, and reads 0 at idle. | UNCERTAIN | source read: FFTLivingWeapons, live there on 1.5.1 and re-read offline on 1.5.2 by its port audit (BB, 2026-10-26); live watch: it equalled the acting slot's address on every call, seq 7 to 12, probe_20261026_212759.jsonl (BB, 2026-10-26) | BB, LW |
| [battle-map-number-byte] | The current battle's map number is a byte at RVA 0x784478, valid 1 to 127. It read 80 on every call of a battle at Araguay Woods. | PROVEN | source read: FFTTreasureMaster Offsets.LiveBattleMapId, listed on the 1.5.2 offsets sheet (BB, 2026-10-27); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify, every call line (BB, 2026-10-28); live tape: s1_retry_act_first_follow_up_move_written_as_act, every call line (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB, sim, LW, TM, HF |

### Turns and battle flow

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [ai-sometimes-acts-before-moving] | The game's own AI sometimes acts before it moves, so a turn can run Act, then Move, then EndTurn. The phase order is not fixed. | PROVEN | live watch: no log, slot 2 on turn 36 of the second battle of 2026-10-26 evening (BB, 2026-10-26); live tape: first_live_battle_hold_fold_and_handbrake#4773 (BB, 2026-10-27); proven in BB 2026-10-26 | BB, sim |
| [move-then-act-turn-skips-endturn] | A turn that moves and then acts ends after the Act with no EndTurn request, its facing coming from the attack. A turn that acts first still gets an EndTurn after its Move. | UNCERTAIN | live watch: slot 3's attack turn, where a facing write armed for EndTurn never fired, probe_20261026_212759.jsonl (BB, 2026-10-26); live watch: turn 4, nothing more asked after the Act, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26) | BB, sim |
| [battle-lost-when-ramza-is-out] | The battle is lost once Ramza is out for good, even with another player unit standing. Game over came when his KO counter ran out with slot 17 still at 392 HP, and again after a Blaster petrified him. | UNCERTAIN | live watch: slot 16, Ramza, at 0 HP from seq 14, probe_20261026_212759.jsonl (BB, 2026-10-26); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#444 (BB, 2026-10-28) | BB, sim |
| [ai-played-turn-keeps-exp-jp] | A player unit whose turns the game's AI plays, its human bit cleared at battle entry, still gains EXP and JP exactly as a hand played turn does. | PROVEN | live watch: no log, the owner's Archer in the third battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [retried-battle-opens-zeroed-request] | When a lost battle is retried, the routine's first call in the new attempt brings an all zero request, with the units on new tiles, a fallen unit back at full HP and the unit table pointer moved. | PROVEN | live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#446 (BB, 2026-10-28); live watch: no log, the owner retried after the game over (BB, 2026-10-28); Patrick agreed 2026-10-29 | BB |
| [stale-act-on-retry-stalls-battle] | Answering the first call of a retried battle with an Act left over from the lost attempt left the game stopped at that turn, window responsive, with no further calls until a relaunch. Whether the stale Act caused it is open. | UNCERTAIN | live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify#446 and no line after it (BB, 2026-10-28) | BB |

### Combat rules

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [act-target-range-not-checked] | The game does not check an Act's target against the ability's range: a Knight's basic attack written at Ramza four tiles away hit him as if adjacent, though the range highlight showed only the adjacent tiles. | PROVEN | live watch: no log, slot 2 at (9,5) against Ramza at (7,7) in the second battle of 2026-10-26 evening (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [self-centred-act-ignores-target-tile] | A self centred area ability fires around its user whatever target tile the Act names: ability 321 written with target (1,1) still hit both player units beside its user, and one countered. | PROVEN | live watch: turn 4 and the owner's view, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); proven in BB 2026-10-26 | BB |

### Maps and movement

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [move-unreachable-tile-not-walked] | The game checks a Move request's destination itself: a tile the unit cannot reach is not walked to, the unit stays where it was, and the turn goes on with no crash or teleport. | PROVEN | live watch: no log, the step 0 edit of X 6 to 7 (BB, 2026-10-26); live watch: turn 2, slot 4 sent to (5,12) stayed put, brain/probe_20261026_230258.jsonl, a log lost on 2026-10-27 (BB, 2026-10-26); live tape: first_driver_battle_stub_then_opus_plays_the_enemy#6214, one of eight written moves that did not land (BB, 2026-10-27); proven in BB 2026-10-26 | BB, sim |
| [move-unreachable-tile-asked-again] | After refusing a Move to an on map tile the unit cannot reach, the game asks for the Move again with its own pick back in the buffer. | UNCERTAIN | live watch: no log, step 0, together's panel popped again with the stock bytes refilled (BB, 2026-10-26) | BB |
| [move-off-map-tile-no-op] | A Move request to an off map tile (X and Y 0x3F) is a no op: the unit enters move mode, does not move, and about 1.2 s later the game asks for EndTurn, with no re-ask, teleport or crash. | PROVEN | live watch: seq 254 and 255 of probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [move-to-own-tile-stays] | A Move request to the unit's own tile is taken as a stay: the unit stays and the game goes on to the next phase, seven times out of seven in one battle. | PROVEN | live tape: first_driver_battle_stub_then_opus_plays_the_enemy#11630 (BB, 2026-10-27); live tape: first_driver_battle_stub_then_opus_plays_the_enemy#11632 (BB, 2026-10-27); Patrick agreed 2026-10-27 | BB, sim |
| [reach-by-walk-route-and-climb] | Whether a unit can reach a tile goes by its walking route and its climb, not grid distance: a tile 3 grid steps away but 5 walking steps round a tree and unwalkable tiles was refused six times to an Archer, and a climb of 6 was refused twice. Move 3 and Jump 3 were assumed, not read. | UNCERTAIN | live tape: first_driver_battle_stub_then_opus_plays_the_enemy#6214, #9422, #13778, #15398, #17729 and #18603 for slot 1, #10457 and #12385 for slots 2 and 8 (BB, 2026-10-27); game table: heights from the MAP080 mesh in data/enhanced/0002.pac (BB, 2026-10-27) | BB, sim |
| [map-files-in-0002-pac] | The battle maps live in data/enhanced/0002.pac under fftpack/map in the PSX format: the GNS index, its 20 byte records intact but the CD sector fields replaced by a running index, and the mesh and texture resources under their PSX numbers. | UNCERTAIN | game table: data/enhanced/0002.pac fftpack/map, read by a parser (BB, 2026-10-27) | BB, sim |
| [map-mesh-terrain-psx-layout] | Each map mesh keeps the PSX layout: a 196 byte pointer header, and the terrain at pointer 0x68 as two levels of 256 tiles of 8 bytes (surface, height, depth and slope height, slope type, thickness, walk and cursor flags). | UNCERTAIN | game table: every mesh in data/enhanced/0002.pac (BB, 2026-10-27) | BB, sim |
| [map-files-over-ganesha-json] | The game's own map files, not fft-map-json, are the truth for terrain. That Ganesha derived JSON, which FFTHandsFree ships, matches on seven fields per tile for 96 of 122 maps and differs on a few tiles or in size for the rest. | UNCERTAIN | game table: every map in data/enhanced/0002.pac against fft-map-json (BB, 2026-10-27) | BB, sim |
| [map-numbers-of-named-battles] | Araguay Woods is MAP080, Dugeura Pass MAP086, the Orbonne book storage fourth floor MAP060 and Zeklaus Desert MAP076. | UNCERTAIN | game table: every stock destination on four tapes is a walkable level 0 tile of the named map, and MAP076 alone of 122 fits the first live battle (BB, 2026-10-27); source read: FFTHandsFree's map id table, agreeing on 80, 86 and 76 (BB, 2026-10-27); live tape: s1_conversions_hand_mode_araguay_woods_ending_in_petrify, map byte 80 at Araguay Woods (BB, 2026-10-28) | BB |

### Menus, screens and text

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [cleared-human-bit-shows-guest] | With the human control bit cleared on the party at battle entry, the game plays the party by computer and labels its units Guest. | PROVEN | live watch: Unit Control's Control Player Units left off, brain/probe_20261027_011757.jsonl, a log no longer kept (BB, 2026-10-27); proven in BB 2026-10-27 | BB |

### The exe and its builds

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [denuvo-era-code-forms-differ] | Code in the Denuvo era builds uses other instruction forms than the plain MSVC compile of 1.5.2 no-DRM (xor esi,esi as 31 F6 not 33 F6, mov rbx,rdx as 48 89 D3 not 48 8B DA), so byte patterns and code addresses taken from those builds miss on no-DRM. | UNCERTAIN | exe scan: fftivc.together's 1.5.0 BattleRoutine pattern, zero hits on 1.5.2 no-DRM and one hit in MSVC forms (BB, 2026-10-26); exe scan: FFTHandsFree's DoAction entry 0x1402832F8 is no prologue on no-DRM (BB, 2026-10-26) | BB |
| [doaction-entry-0x1402832f8] | DoAction, FFTHandsFree's action entry, starts at preferred 0x1402832F8 on 1.5.2 no-DRM, where FFTHandsFree verified it live on 1.5. | CONTRADICTED | exe scan: the bytes there are 2f 3d 85 01 on 1.5.2 no-DRM, not a prologue (BB, 2026-10-26); source read: FFTHandsFree, live verified on 1.5 (BB, 2026-10-26) | BB, HF |
| [doaction-body-lea-two-hits] | The lea rdi,[rcx+1A0h] that opens DoAction's body appears twice in the 1.5.2 no-DRM exe, at RVA 0x28329B and RVA 0x30D100. | UNCERTAIN | exe scan: the lea's byte pattern (BB, 2026-10-26) | BB, HF |
| [symbol-map-addresses-other-build] | The code addresses in skeewirt/fftivc-symbol-map belong to another build: on 1.5.2 no-DRM its function entries land mid instruction under every transform tried. Its names still serve. | UNCERTAIN | exe scan: thunks 0x30A468 and 0x2F8548 and the entries of Battle_UnitCommandMode 0x1F76B8, Battle_ActionCommandSelectMode 0x1F20A4, BattleRoutine_ProcessMoveFlagAndTileInfo 0x30AC64 and MarkBattleUnitMovedAndCheckIfCanAct 0x2F2438, under four transforms (BB, 2026-10-26) | BB |
