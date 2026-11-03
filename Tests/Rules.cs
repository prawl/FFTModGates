using System;
using System.IO;
using System.Text.Json;

namespace ModGates.Tests;

/// <summary>
/// The repo's rules.json, the one place that says where its production code, tests and
/// projects are and which ticket prefix its ledger uses. Every shared test reads it from here.
/// </summary>
internal sealed class Rules
{
    public string Prod { get; init; } = "";
    public string Tests { get; init; } = "";
    public string TicketPrefix { get; init; } = "";
    public string[] Projects { get; init; } = Array.Empty<string>();
    public string[] TestProjects { get; init; } = Array.Empty<string>();
    public string ModConfig { get; init; } = "mod/ModConfig.json";
    public string? DevDefine { get; init; }
    public string[] TempPrefixes { get; init; } = Array.Empty<string>();
    public string[] TempKeep { get; init; } = Array.Empty<string>();
    public string LoggingDoc { get; init; } = "docs/LOGGING.md";
    public string[] ConsoleAllowlist { get; init; } = Array.Empty<string>();
    public string[] FenceExemptFiles { get; init; } = Array.Empty<string>();

    private static Rules? _loaded;

    public static Rules Load() => _loaded ??= Read(RepoRoot.Locate());

    public string ProdDir => Path.Combine(RepoRoot.Locate(), Prod.TrimEnd('/'));
    public string TestsDir => Path.Combine(RepoRoot.Locate(), Tests.TrimEnd('/'));

    private static Rules Read(string root)
    {
        string json = File.ReadAllText(Path.Combine(root, "rules.json"));
        var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true, ReadCommentHandling = JsonCommentHandling.Skip };
        var rules = JsonSerializer.Deserialize<Rules>(json, options) ?? throw new InvalidDataException("rules.json is empty");
        if (rules.Prod.Length == 0 || rules.Tests.Length == 0 || rules.TicketPrefix.Length == 0)
            throw new InvalidDataException("rules.json needs prod, tests and ticketPrefix");
        return rules;
    }
}
