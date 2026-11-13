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
| [battle-routine-entry] | The game asks what a computer run unit does next through one routine, BattleRoutine(unit index, action request), at RVA 0x31F130. | PROVEN | exe scan: MSVC form pattern, one hit at RVA 0x31F130 (BB, 2026-10-26); live watch: hooked there, probe_20261026_212759.jsonl (BB, 2026-10-26); source read: dicene/fftivc.together Mod.cs (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-unit-index-is-slot] | The routine's first argument is the acting unit's slot in the battle unit array. | PROVEN | live watch: acting.ptr equals actor_ptr on every call, seq 7 to 12, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-return-two-reasks] | Returning 2 from the routine means not decided yet. The game asks again once a frame, about every 16.6 ms, keeps running, and leaves the request buffer as it was. Returning 0 means decided, and the request in the buffer runs as written. | PROVEN | live watch: 189 asks over 3.2 s with the buffer identical on all 189, seq 56 to 248, probe_20261026_212759.jsonl (BB, 2026-10-26); source read: dicene/fftivc.together Mod.cs (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [battle-routine-covers-every-ai-turn] | The same routine decides enemy turns, a player unit on the game's Auto-Battle, and a player unit whose human bit was cleared from outside. | PROVEN | live watch: seq 14 to 24 of probe_20261026_212759.jsonl and session probe_20261026_214658 (BB, 2026-10-26); proven in BB 2026-10-26 | BB |

### The action request

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [action-request-move-destination] | A Move request (byte +0 is 0) carries the destination tile's X at +4 and Y at +8, each a u16. | PROVEN | live watch: three walks ended on the requested tile by the unit's grid bytes +0x4F and +0x50, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |
| [action-request-facing-byte] | Byte +C of a Move or EndTurn request holds the unit's facing, 0 to 3, and writing it on the EndTurn request sets the facing the unit ends its turn with. | PROVEN | live watch: the step 0 edit and the seq 29 overwrite, probe_20261026_212759.jsonl (BB, 2026-10-26); proven in BB 2026-10-26 | BB |

### The battle unit record

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [unit-move-jump-bytes] | A unit's Move and Jump, gear and movement abilities counted, are bytes +0x42 and +0x43 of its battle unit record. | PROVEN | live tape: gear_battle_four_known_move_and_jump_pairs_at_dial_100.jsonl.gz#10 (BB, 2026-11-01); PSX doc: FFHacktics wiki Battle Stats (BB, 2026-11-01); Patrick agreed 2026-11-01 | BB |
| [unit-human-control-bit] | Bit 0x08 of a unit's Flags2, at +0x05 and mirrored at +0x1EE, means a human picks its actions. Setting it on both bytes from outside opens the player's menu on an enemy, and clearing it hands the turn to the AI. | PROVEN | live tape: live_check_act_first_walks_and_mid_turn_loss_retries_clean#2585 (BB, 2026-10-29); source read: dicene/fftivc.unitcontrol BattleUnits.cs (BB, 2026-10-26); live watch: FFTMultiplayer PuppetHold held a whole enemy team human for a battle on 1.5 (BB, 2026-10-26); Patrick agreed 2026-10-29 | BB, MP |

### Battle state

| Id | Fact | Mark | Evidence | Leaned on by |
|---|---|---|---|---|
| [battle-mode-byte-turn-sides] | The battle mode byte at preferred 0x1409069A0 reads 3 on the player's turn and 5 on the enemy's, the reading carried over from 1.5. | CONTRADICTED | live watch: it read 3 during enemy turns, probe_20261026_212759.jsonl (BB, 2026-10-26); source read: FFTHandsFree on 1.5 for the old reading (BB, 2026-10-26) | BB, LW, TM, HF, MP |
