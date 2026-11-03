using System;

namespace ModGates.Logging;

/// <summary>
/// What one mod tells the shared logger at Init. The file lands in ModDir as FileStem.log and
/// every line opens with Prefix. The hooks are optional. A mod with a flight recorder passes its
/// flush as ErrorFlush, and one that counts quiet faults passes FaultNote.
/// </summary>
internal sealed record LogSetup(
    string ModDir,
    string Prefix,
    string FileStem,
    Action<string>? FaultNote = null,
    Action? ErrorFlush = null)
{
    /// <summary>The logger a mod gets when it logs before calling Init.</summary>
    public static LogSetup Default(string modDir) => new(modDir, "[Mod]", "mod");
}
