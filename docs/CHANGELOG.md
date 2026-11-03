# Changelog (work-ledger exits)

STATUS: CONTRACT (machine-checked by TodoContractTests)

Where docs/TODO.md items land when they ship, die, or retract; newest first within a cycle.
Entry first line: `- [MG-<n>] SHIPPED <hash> YYYY-MM-DD: <summary>`, or WONTFIX / RETRACTED
with a date and no hash.

## 0.1 cycle

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
