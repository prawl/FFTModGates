using System;

namespace ModGates.Logging;

/// <summary>
/// A logger bound to one verb and one armed predicate, built by ModLogger.For. Info and Warn
/// demote to Debug while the module is not armed, so call sites never branch on armed
/// themselves. Debug is never gated; file evidence is always worth keeping.
/// </summary>
internal readonly struct ScopedLogger
{
    private readonly LogVerb _verb;
    private readonly Func<bool> _armed;

    internal ScopedLogger(LogVerb verb, Func<bool> armed)
    {
        _verb = verb;
        _armed = armed;
    }

    public void Info(string message)
    {
        if (SafeArmed()) ModLogger.Event(_verb, message);
        else ModLogger.Debug(_verb, message);
    }

    public void Warn(string message)
    {
        if (SafeArmed()) ModLogger.Warn(_verb, message);
        else ModLogger.Debug(_verb, message);
    }

    public void Debug(string message) => ModLogger.Debug(_verb, message);

    /// <summary>An armed predicate may read game memory; a throw there must not take the log line with it.</summary>
    private bool SafeArmed()
    {
        try { return _armed(); } catch { return false; }
    }
}
