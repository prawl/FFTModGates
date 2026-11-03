using System;

namespace ModGates.Logging;

/// <summary>
/// The static logging facade. Every call site logs through the typed members here (Event, Warn,
/// Error, Debug, the WithTrace pairs, or a ScopedLogger from For), never against ILogger or a
/// concrete logger. Instance is the test seam. Production creates a FileConsoleLogger lazily
/// from the setup Init was given.
/// </summary>
internal static class ModLogger
{
    private static ILogger? _logger;
    private static readonly object _lock = new();
    private static LogSetup? _setup;

    /// <summary>Called once from Mod.cs before anything else logs, so the log file lands beside the DLL.</summary>
    public static void Init(string modDir, string prefix, string fileStem, Action<string>? faultNote = null, Action? errorFlush = null)
        => Init(new LogSetup(modDir, prefix, fileStem, faultNote, errorFlush));

    public static void Init(LogSetup setup)
    {
        lock (_lock) { _setup = setup; _logger = null; }
    }

    public static ILogger Instance
    {
        get
        {
            if (_logger == null)
                lock (_lock)
                    _logger ??= new FileConsoleLogger(_setup ?? LogSetup.Default(Environment.CurrentDirectory));
            return _logger;
        }
        set { lock (_lock) { _logger = value; } }
    }

    /// <summary>The console volume threshold. The file always gets everything.</summary>
    public static LogLevel LogLevel
    {
        get => Instance.LogLevel;
        set => Instance.LogLevel = value;
    }

    public static void Event(LogVerb verb, string message) => Instance.Log(verb, message);
    public static void Warn(LogVerb verb, string message) => Instance.LogWarning(verb, message);
    public static void Error(LogVerb verb, string message) => Instance.LogError(verb, message);
    public static void Error(LogVerb verb, string message, Exception exception) => Instance.LogError(verb, message, exception);
    public static void Debug(LogVerb verb, string message) => Instance.LogDebug(verb, message);

    /// <summary>A plain Info sentence for the console, paired with a trace line that carries the ids and hex for the file.</summary>
    public static void EventWithTrace(LogVerb verb, string message, string traceDetail)
    {
        Event(verb, message);
        Debug(LogVerb.Trace, traceDetail);
    }

    /// <summary>The same pair at Warning tier.</summary>
    public static void WarnWithTrace(LogVerb verb, string message, string traceDetail)
    {
        Warn(verb, message);
        Debug(LogVerb.Trace, traceDetail);
    }

    /// <summary>A logger bound to one verb and one armed predicate; Info and Warn demote to Debug while unarmed.</summary>
    public static ScopedLogger For(LogVerb verb, Func<bool> armed) => new(verb, armed);

    /// <summary>Clears the console's per-battle dedup memory on every battle edge the mod can see.</summary>
    public static void NoteBattleEdge() => Instance.NoteBattleEdge();

    /// <summary>Test seam. Drops the current logger and setup so the next call recreates the default.</summary>
    public static void Reset()
    {
        lock (_lock) { _logger = null; _setup = null; }
    }

    /// <summary>Test seam. Swaps in the logger that swallows everything.</summary>
    public static void UseNullLogger() => Instance = NullLogger.Instance;
}
