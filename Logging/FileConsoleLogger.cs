using System;
using System.Collections.Generic;
using System.IO;

namespace ModGates.Logging;

/// <summary>
/// The production logger with two sinks. The file (FileStem.log, rotated at launch to
/// FileStem.prev.log) gets every message of every tier, each line stamped to the millisecond.
/// The console gets a message only at or above the threshold, and only the first time its
/// (level, verb, message) identity appears in a battle; NoteBattleEdge clears that memory. The
/// file line always carries the verb bracket; the console drops it at Info tier, the tier a
/// player reads as prose. A sink that throws never takes the call down with it; the fault goes
/// to the mod's note hook, and every Error asks the mod's flush hook to keep its recorder.
/// </summary>
internal sealed class FileConsoleLogger : ILogger
{
    private readonly string _prefix;
    private readonly Action<string> _consoleSink;
    private readonly Action<string> _fileSink;
    private readonly Action<string> _faultNote;
    private readonly Action _errorFlush;
    private readonly HashSet<(LogLevel Level, LogVerb Verb, string Message)> _consoleSeenThisBattle = new();

    /// <summary>One lock around Write and NoteBattleEdge. The game thread logs from inside a hook
    /// while other threads log from their own, and the dedup set is a plain HashSet.</summary>
    private readonly object _gate = new();

    public LogLevel LogLevel { get; set; } = LogLevel.Info;

    public FileConsoleLogger(LogSetup setup)
        : this(Console.WriteLine, MakeFileSink(setup), setup.Prefix, setup.FaultNote, setup.ErrorFlush) { }

    /// <summary>Test seam. Injected sinks keep tests away from the real console and disk.</summary>
    internal FileConsoleLogger(Action<string> consoleSink, Action<string> fileSink, string prefix = "[Mod]",
        Action<string>? faultNote = null, Action? errorFlush = null)
    {
        _consoleSink = consoleSink;
        _fileSink = fileSink;
        _prefix = prefix;
        _faultNote = faultNote ?? (_ => { });
        _errorFlush = errorFlush ?? (() => { });
    }

    /// <summary>Rotates the previous launch's log aside, then appends one line per call. A locked
    /// or read-only folder leaves the mod with console logging only instead of no mod.</summary>
    private static Action<string> MakeFileSink(LogSetup setup)
    {
        Action<string> note = setup.FaultNote ?? (_ => { });
        string file = Path.Combine(setup.ModDir, setup.FileStem + ".log");
        try
        {
            if (File.Exists(file))
                File.Move(file, Path.Combine(setup.ModDir, setup.FileStem + ".prev.log"), true);
        }
        catch { note("FileConsoleLogger.Rotate"); }
        return line => File.AppendAllText(file, line + "\n");
    }

    public void Log(LogVerb verb, string message) => Write(LogLevel.Info, verb, message);
    public void LogWarning(LogVerb verb, string message) => Write(LogLevel.Warning, verb, message);
    public void LogDebug(LogVerb verb, string message) => Write(LogLevel.Debug, verb, message);

    public void LogError(LogVerb verb, string message)
    {
        Write(LogLevel.Error, verb, message);
        Guarded(_errorFlush, "FileConsoleLogger.ErrorFlush");
    }

    public void LogError(LogVerb verb, string message, Exception exception)
    {
        Write(LogLevel.Error, verb, message);
        if (exception != null)
            Write(LogLevel.Error, verb, $"  {exception.GetType().Name}: {exception.Message}");
        Guarded(_errorFlush, "FileConsoleLogger.ErrorFlush");
    }

    public void NoteBattleEdge()
    {
        lock (_gate) { _consoleSeenThisBattle.Clear(); }
    }

    private void Write(LogLevel level, LogVerb verb, string message)
    {
        lock (_gate)
        {
            string levelToken = LevelToken(level);
            string body = message ?? string.Empty;
            string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
            string verbBracket = $"[{verb.Token()}] ";
            Guarded(() => _fileSink($"{_prefix} [{timestamp}] [{levelToken}] {verbBracket}{body}"), "FileConsoleLogger.File");
            if (level >= LogLevel && _consoleSeenThisBattle.Add((level, verb, body)))
            {
                bool showVerb = level != LogLevel.Info;
                Guarded(() => _consoleSink($"{_prefix} [{timestamp}] [{levelToken}] {(showVerb ? verbBracket : "")}{body}"), "FileConsoleLogger.Console");
            }
        }
    }

    private void Guarded(Action step, string site)
    {
        try { step(); }
        catch { _faultNote(site); }
    }

    private static string LevelToken(LogLevel level) => level switch
    {
        LogLevel.Debug => "DEBUG",
        LogLevel.Info => "INFO",
        LogLevel.Warning => "WARN",
        LogLevel.Error => "ERROR",
        _ => level.ToString().ToUpperInvariant(),
    };
}
