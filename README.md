# FFTModGates

One rulebook for every FFT mod. Each mod carries a copy of this folder, runs the same checks on
every build, and keeps only its own starting numbers. From the day a mod takes it, no number a
gate measures can get worse.

## What is in here

| Folder | What it holds | What a mod supplies |
| --- | --- | --- |
| `Logging/` | The logger every mod writes through (ILogger, ModLogger, FileConsoleLogger, NullLogger, ScopedLogger), compiled into the mod's own DLL as linked source | Its `LogVerb.cs` in the `ModGates.Logging` namespace, with a `Trace` member |
| `Tests/` | The shared contract tests and the helpers they read the repo through, compiled into the mod's test project | Its `rules.json`, baselines and allowlists |
| `tools/health.py` | The code health report, ratchet and floor | Nothing beyond `rules.json` |
| `pipeline/gates.ps1` | The gate functions: format, unit tests, health, temp leftovers | Its own gates below the dot-source line |
| `Directory.Build.targets` | Warnings as errors and code style in the build | One import line |
| `.editorconfig` | The code style the build enforces | A byte-for-byte copy at its root |

`Selftest/` compiles the package the way a mod does and runs it against this repo's own rules, so
the package is held to the rules it enforces.

## How a mod takes it

Everything below is one commit. No gameplay code moves.

1. Vendor the folder as a subtree, so worktrees and fresh clones need nothing extra:

   ```
   git subtree add --prefix gates https://github.com/prawl/FFTModGates.git main --squash
   ```

2. Add `rules.json` at the repo root:

   ```json
   {
     "prod": "LivingWeapon/",
     "tests": "LivingWeapon.Tests/",
     "ticketPrefix": "LW",
     "projects": ["LivingWeapon/LivingWeapon.csproj", "LivingWeapon.Tests/LivingWeapon.Tests.csproj"],
     "testProjects": ["LivingWeapon.Tests/LivingWeapon.Tests.csproj"],
     "modConfig": "mod/ModConfig.json",
     "devDefine": "LWDEV",
     "tempPrefixes": ["lw_"],
     "tempKeep": []
   }
   ```

   `modConfig` is the JSON file whose `ModVersion` names the release, or a plain file holding the
   version. `devDefine` is optional and names the `#if` that compiles a dev spike out of release
   builds. `tempPrefixes` are the temp folder names the repo's tests create; `tempKeep` any fixed
   one a test rebuilds every run.

3. Compile the logger into the mod and the tests into the test project, as linked source:

   ```xml
   <ItemGroup>
     <Compile Include="..\gates\Logging\*.cs" Link="Gates\Logging\%(Filename)%(Extension)" />
   </ItemGroup>
   ```

   ```xml
   <ItemGroup>
     <Compile Include="..\gates\Tests\**\*.cs" Link="Gates\Tests\%(RecursiveDir)%(Filename)%(Extension)" />
   </ItemGroup>
   ```

   The mod's `LogVerb.cs` moves into the `ModGates.Logging` namespace, one file holds
   `global using ModGates.Logging;`, and `Mod.cs` calls
   `ModLogger.Init(modDir, "[Living Weapons]", "livingweapon")`. A mod with a flight recorder
   passes its flush as the `errorFlush` hook, and one that counts quiet faults passes `faultNote`.

4. Import the build settings from a root `Directory.Build.targets`:

   ```xml
   <Project>
     <Import Project="gates\Directory.Build.targets" />
   </Project>
   ```

   Then delete the same settings from the csproj files; the shared file owns them now.

5. Load the gate functions at the top of `tools/pipeline.ps1` and keep the repo's own gates below:

   ```powershell
   . "$PSScriptRoot\..\gates\pipeline\gates.ps1"
   ```

6. Copy `gates/.editorconfig` to the repo root. The style contract checks the two match.

## Taking a newer rulebook

```
git subtree pull --prefix gates https://github.com/prawl/FFTModGates.git main --squash
```

The commit is the moment the mod takes the new rules. `gates/VERSION` says which, and every build
prints it. Nothing moves on its own.

## What stays in each mod

Tape tests, data pipeline gates, and the docs, readme, proof claim and pipeline manifest
contracts, because each one checks that mod's own files.

## Working on this repo

`.\Check.ps1` runs every gate here. The ledger is `docs/TODO.md` and `docs/CHANGELOG.md` with the
MG id prefix.
