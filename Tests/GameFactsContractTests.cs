using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;

namespace ModGates.Tests;

/// <summary>
/// The shared game fact list, docs/GAME_FACTS.md here and gates/docs/GAME_FACTS.md in a mod. Every
/// fact row has five cells, an id used once, one of the five marks, sources of a kind the list names
/// and readers from its repo table. A PROVEN row carries a live source and Patrick's word.
/// </summary>
public class GameFactsContractTests
{
    private static readonly HashSet<string> Kinds = new() { "live tape", "live watch", "exe scan", "source read" };
    private static readonly HashSet<string> Repos = new() { "BB", "LW" };

    private const string Good = "| [a-fact] | The game does a thing. | UNCERTAIN | exe scan: one hit at RVA 0x10 (BB, 2026-10-26) | BB |";

    [Theory]
    [InlineData(Good, "")]
    [InlineData("| [a-fact] | Seen. | PROVEN | live watch: no log (BB, 2026-10-26); Patrick agreed 2026-10-27 | BB, LW |", "")]
    [InlineData("| [a-fact] | Seen. | PROVEN | live tape: t.jsonl.gz#4 (LW, 2026-10-17); proven in LW 2026-10-17 | LW |", "")]
    [InlineData("| [a-fact] | Gap. | NOT MODELED | source read: tools/sim/clock.py (BB, 2026-11-12) | BB |", "")]
    [InlineData("| [A_Fact] | The game does a thing. | UNCERTAIN | exe scan: x (BB, 2026-10-26) | BB |", "id")]
    [InlineData("| [a-fact] |  | UNCERTAIN | exe scan: x (BB, 2026-10-26) | BB |", "fact")]
    [InlineData("| [a-fact] | Thing. | LIKELY | exe scan: x (BB, 2026-10-26) | BB |", "mark")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | a hunch: x (BB, 2026-10-26) | BB |", "source")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | exe scan: x | BB |", "source")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | exe scan: x (TM, 2026-10-26) | BB |", "source")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | Patrick agreed 2026-10-26 | BB |", "no source")]
    [InlineData("| [a-fact] | Seen. | PROVEN | live watch: no log (BB, 2026-10-26) | BB |", "agreed")]
    [InlineData("| [a-fact] | Read. | PROVEN | exe scan: x (BB, 2026-10-26); Patrick agreed 2026-10-27 | BB |", "live")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | exe scan: x (BB, 2026-10-26) | BB, TM |", "reader")]
    [InlineData("| [a-fact] | Thing. | UNCERTAIN | exe scan: x (BB, 2026-10-26) |  |", "reader")]
    [InlineData("| [a-fact] | A or B. | UNCERTAIN | exe scan: x (BB, 2026-10-26) | BB | extra |", "cells")]
    public void A_row_is_refused_for_the_fault_named(string row, string fault)
    {
        var faults = FactList.Faults(FactList.Cells(row), Kinds, Repos);
        if (fault.Length == 0)
            Assert.True(faults.Count == 0, string.Join("; ", faults));
        else
            Assert.True(faults.Any(f => f.Contains(fault)), $"wanted a fault naming '{fault}', got: {string.Join("; ", faults)}");
    }

    [Fact]
    public void The_tables_are_read_from_the_list_itself()
    {
        string[] doc =
        {
            "## Evidence kinds", "", "| Kind | What it is | Cite as |", "|---|---|---|", "| live tape | t | c |",
            "", "## Repos", "", "| Short | Repo |", "|---|---|", "| BB | FFTBattleBrain |", "",
            "## Facts", "", "### An area", "", FactList.Header, "|---|---|---|---|---|", Good, "", "after the table",
        };
        Assert.Equal(new[] { "live tape" }, FactList.FirstColumn(doc, "## Evidence kinds"));
        Assert.Equal(new[] { "BB" }, FactList.FirstColumn(doc, "## Repos"));
        Assert.Equal(new[] { Good }, FactList.Rows(doc).Select(r => r.Line));
    }

    [Fact]
    public void Every_fact_row_keeps_the_shape()
    {
        string[]? doc = FactList.Load();
        if (doc is null) return;
        var kinds = FactList.FirstColumn(doc, "## Evidence kinds").ToHashSet();
        var repos = FactList.FirstColumn(doc, "## Repos").ToHashSet();
        var rows = FactList.Rows(doc).ToList();
        Assert.True(rows.Count > 0, $"No fact table found. A fact table opens with the header row {FactList.Header}");
        var bad = rows.Select(r => (r.Number, Faults: FactList.Faults(FactList.Cells(r.Line), kinds, repos)))
            .Where(r => r.Faults.Count > 0).Select(r => $"line {r.Number}: {string.Join("; ", r.Faults)}").ToList();
        Assert.True(bad.Count == 0, "Fact rows out of shape (docs/GAME_FACTS.md says the shape):\n" + string.Join("\n", bad));
    }

    [Fact]
    public void Every_fact_id_is_used_once_and_every_table_in_the_facts_part_is_a_fact_table()
    {
        string[]? doc = FactList.Load();
        if (doc is null) return;
        var twice = FactList.Rows(doc).GroupBy(r => FactList.Cells(r.Line).FirstOrDefault() ?? "").Where(g => g.Count() > 1)
            .Select(g => $"{g.Key} on lines {string.Join(", ", g.Select(r => r.Number))}").ToList();
        Assert.True(twice.Count == 0, "Fact ids used more than once. An id is never reused:\n" + string.Join("\n", twice));
        var strays = FactList.StrayHeaders(doc).ToList();
        Assert.True(strays.Count == 0, $"Tables under ## Facts whose header is not {FactList.Header}, so their rows go unchecked:\n" + string.Join("\n", strays));
    }
}

/// <summary>Reads the fact list's tables. Its kinds and repos come from the list's own tables, so adding one is a doc edit.</summary>
internal static class FactList
{
    public const string Header = "| Id | Fact | Mark | Evidence | Leaned on by |";

    // A fact past this many characters is almost always two claims sharing a row.
    private const int FactCap = 500;

    private static readonly HashSet<string> Marks = new() { "PROVEN", "UNCERTAIN", "CONTRADICTED", "WALLED", "NOT MODELED" };
    private static readonly HashSet<string> LiveKinds = new() { "live tape", "live watch" };
    private static readonly Regex Id = new(@"^\[[a-z0-9]+(-[a-z0-9]+)*\]$");
    private static readonly Regex Agreed = new(@"^(Patrick agreed|proven in [A-Z]+) \d{4}-\d{2}-\d{2}$");
    private static readonly Regex Source = new(@"^([A-Za-z ]+): .+ \(([A-Za-z]+), \d{4}-\d{2}-\d{2}\)$");

    public static string[]? Load()
    {
        string root = RepoRoot.Locate();
        bool isRulebook = File.Exists(Path.Combine(root, "MANIFEST.sha256"));
        string path = isRulebook ? Path.Combine(root, "docs", "GAME_FACTS.md") : Path.Combine(root, "gates", "docs", "GAME_FACTS.md");
        if (isRulebook) Assert.True(File.Exists(path), "The rulebook carries docs/GAME_FACTS.md and it is gone");
        return File.Exists(path) ? File.ReadAllLines(path) : null;
    }

    public static string[] Cells(string line)
    {
        string t = line.Trim();
        return t.StartsWith('|') && t.EndsWith('|') ? t[1..^1].Split('|').Select(c => c.Trim()).ToArray() : Array.Empty<string>();
    }

    public static IEnumerable<string> FirstColumn(string[] doc, string heading)
        => Section(doc, heading).Where(l => l.StartsWith('|')).Skip(2).Select(l => Cells(l)[0]);

    public static IEnumerable<(int Number, string Line)> Rows(string[] doc)
    {
        bool inTable = false;
        for (int i = 0; i < doc.Length; i++)
        {
            if (doc[i].Trim() == Header && i + 1 < doc.Length) { inTable = true; i++; continue; }
            if (!doc[i].StartsWith('|')) inTable = false;
            else if (inTable) yield return (i + 1, doc[i]);
        }
    }

    public static IEnumerable<string> StrayHeaders(string[] doc)
    {
        var facts = Section(doc, "## Facts").ToArray();
        for (int i = 0; i < facts.Length; i++)
            if (facts[i].StartsWith('|') && (i == 0 || !facts[i - 1].StartsWith('|')) && facts[i].Trim() != Header)
                yield return facts[i];
    }

    public static List<string> Faults(string[] cells, ISet<string> kinds, ISet<string> repos)
    {
        if (cells.Length != 5) return new() { $"has {cells.Length} cells, wants 5 (a pipe inside a cell splits it)" };
        var faults = new List<string>();
        if (!Id.IsMatch(cells[0])) faults.Add($"id {cells[0]} is not a kebab case name in brackets");
        if (cells[1].Length == 0 || cells[1].Length > FactCap) faults.Add($"fact is {cells[1].Length} characters, wants 1 to {FactCap}");
        if (!Marks.Contains(cells[2])) faults.Add($"mark {cells[2]} is not one of {string.Join(", ", Marks)}");
        var parts = cells[3].Split(';').Select(p => p.Trim()).ToList();
        var sources = parts.Where(p => !Agreed.IsMatch(p)).ToList();
        foreach (var p in sources)
        {
            var m = Source.Match(p);
            if (!m.Success || !kinds.Contains(m.Groups[1].Value) || !repos.Contains(m.Groups[2].Value))
                faults.Add($"source '{p}' wants a known kind, a colon, and (repo, YYYY-MM-DD) at its end");
        }
        if (sources.Count == 0) faults.Add("evidence names no source");
        if (cells[2] == "PROVEN" && !parts.Any(p => Agreed.IsMatch(p))) faults.Add("PROVEN without 'Patrick agreed' or 'proven in' and a day");
        if (cells[2] == "PROVEN" && !sources.Any(p => LiveKinds.Contains(Source.Match(p).Groups[1].Value))) faults.Add("PROVEN without a live source");
        var readers = cells[4].Split(',').Select(r => r.Trim()).ToList();
        if (readers.Any(r => !repos.Contains(r))) faults.Add($"reader list '{cells[4]}' names a repo missing from the repo table");
        return faults;
    }

    private static IEnumerable<string> Section(string[] doc, string heading)
        => doc.SkipWhile(l => l.Trim() != heading).Skip(1).TakeWhile(l => !l.StartsWith("## "));
}
