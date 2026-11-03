# Changelog (work-ledger exits)

STATUS: CONTRACT (machine-checked by TodoContractTests)

Where docs/TODO.md items land when they ship, die, or retract; newest first within a cycle.
Entry first line: `- [MG-<n>] SHIPPED <hash> YYYY-MM-DD: <summary>`, or WONTFIX / RETRACTED
with a date and no hash.

## 0.1 cycle

- [MG-1] SHIPPED 304b739 2026-11-02: One rulebook every mod can take, seeded from the best copy of
  each rule. The shared logger, health.py, the gate functions, the build settings and the style
  file live here with no mod's name inside, and the repo checks itself with its own gates.
  (Tech: Logging/ with fault note and error flush hooks, tools/health.py reading rules.json,
  pipeline/gates.ps1, Directory.Build.targets, Selftest/ with 50 tests; 13 of 13 health numbers
  identical on the newest mod's tree.)
