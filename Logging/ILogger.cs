using System;

namespace ModGates.Logging;

/// <summary>
/// The logging contract every mod on the shared gates writes through. ModLogger is the static
/// facade every call site uses, FileConsoleLogger the production implementation, NullLogger the
/// test-only one that swallows everything. Every member names a verb; there is no free-form
/// surface. The mod supplies the LogVerb enum in this namespace, and it must carry a Trace member.
/// </summary>
internal interface ILogger
{
    /// <summary>The console volume threshold. The file sink ignores it and records everything.</summary>
    LogLevel LogLevel { get; set; }

    /// <summary>Info tier. The file line carries the verb bracket; the console line drops it.</summary>
    void Log(LogVerb verb, string message);

    /// <summary>Warning tier. Both sinks carry the verb bracket, since a console paste needs it for triage.</summary>
    void LogWarning(LogVerb verb, string message);

    /// <summary>Error tier. Both sinks carry the verb bracket.</summary>
    void LogError(LogVerb verb, string message);

    /// <summary>Error tier with the exception appended as a second line.</summary>
    void LogError(LogVerb verb, string message, Exception exception);

    /// <summary>Debug tier. Always in the file, on the console only when the threshold is lowered to Debug.</summary>
    void LogDebug(LogVerb verb, string message);

    /// <summary>Clears the console's per-battle dedup memory. The file sink is never deduped.</summary>
    void NoteBattleEdge();
}

/// <summary>Verbosity tiers from most to least verbose. A threshold of N lets the console show
/// any call at tier N or above; None silences the console. The file records everything.</summary>
internal enum LogLevel
{
    Debug = 0,
    Info = 1,
    Warning = 2,
    Error = 3,
    None = 4,
}
