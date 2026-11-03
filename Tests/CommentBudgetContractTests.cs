using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using Xunit;

namespace ModGates.Tests;

/// <summary>
/// The comment budget. A file in the frozen baseline may not grow its comment lines past a small
/// allowance or its longest comment block at all. A new file keeps comments under a third of its
/// code and no block over eight lines. No comment argues, or carries a colon or a dash inside a
/// sentence. Every file opens with one short plain sentence. The baseline lives in comments.json.
/// </summary>
public class CommentBudgetContractTests
{
    private const double NewFileMaxRatio = 1.0 / 3.0;
    private const int NewFileMaxBlock = 8;
    private const double GrowthAllowance = 0.10;
    private const int GrowthFloor = 3;
    private const int MaxFirstSentence = 110;

    private static readonly Regex TellRegex = new(
        @"load-bearing|deliberately|by design|review blocker|verifier NIT|owner ruling|owner direction|precedent|doctrine",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    private static bool HasDirSegment(string path, string segment)
        => path.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar).Any(part => string.Equals(part, segment, StringComparison.OrdinalIgnoreCase));

    private static IEnumerable<(string Key, string FullPath)> ProductionFiles()
    {
        var rules = Rules.Load();
        foreach (var f in Directory.GetFiles(rules.ProdDir, "*.cs", SearchOption.AllDirectories).Where(f => !HasDirSegment(f, "obj") && !HasDirSegment(f, "bin")).OrderBy(f => f))
            yield return ($"{rules.ProdName}/{Path.GetFileName(f)}", f);
    }

    internal readonly record struct Measure(int CommentLines, int CodeLines, int MaxBlock, int Colons, int Dashes, List<string> Tells);

    /// <summary>A comment line starts with //, /* or *. A trailing comment counts toward tells, colons and dashes only.</summary>
    internal static Measure MeasureText(string text)
    {
        int comment = 0, code = 0, run = 0, maxRun = 0, colons = 0, dashes = 0;
        var tells = new List<string>();
        foreach (var raw in text.Split('\n'))
        {
            string s = raw.Trim();
            if (s.Length == 0) continue;
            string? commentText = null;
            if (s.StartsWith("//") || s.StartsWith("/*") || s.StartsWith("*"))
            {
                comment++; run++; maxRun = Math.Max(maxRun, run); commentText = s;
            }
            else
            {
                code++; run = 0;
                int k = raw.IndexOf(" //", StringComparison.Ordinal);
                if (k >= 0) commentText = raw[k..];
            }
            if (commentText is null) continue;
            string body = Regex.Replace(commentText, @"<[^>]+>|""[^""]*""|`[^`]*`", "#");
            body = Regex.Replace(body, @"\b0x[0-9A-Fa-f]+\b|\b\d+:\d+\b|\b[\w.]+\.(cs|py|md|ps1):\d+", "#");
            string prose = Regex.Replace(body, @"^(?:///|//|/\*|\*)\s*-\s", "");
            colons += Regex.Matches(body, @"\w: ").Count;
            dashes += Regex.Matches(prose, @"(?<=[A-Za-z0-9)]) - (?=[A-Za-z0-9(])|—| -- ").Count;
            foreach (Match m in TellRegex.Matches(body)) tells.Add(m.Value);
        }
        return new Measure(comment, code, maxRun, colons, dashes, tells);
    }

    private static Dictionary<string, Measure> Current()
        => ProductionFiles().ToDictionary(p => p.Key, p => MeasureText(File.ReadAllText(p.FullPath)), StringComparer.Ordinal);

    private static Dictionary<string, int[]> LoadBaseline()
    {
        string path = Rules.Load().BaselinePath("comments.json");
        if (!File.Exists(path)) return new Dictionary<string, int[]>(StringComparer.Ordinal);
        return JsonSerializer.Deserialize<Dictionary<string, int[]>>(File.ReadAllText(path)) ?? new Dictionary<string, int[]>(StringComparer.Ordinal);
    }

    [Fact]
    public void Scan_covers_the_runtime_and_keys_are_unique()
    {
        var keys = ProductionFiles().Select(p => p.Key).ToList();
        Assert.True(keys.Count > 0, "production sweep found no file");
        var dupes = keys.GroupBy(k => k).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
        Assert.True(dupes.Count == 0, "two production files share a filename, which would merge their rows: " + string.Join(", ", dupes));
    }

    [Theory]
    [InlineData("// plain words\nint x = 1;\n", 1, 1, 1, 0, 0, 0)]
    [InlineData("/// <summary>a: b</summary>\n/// second\n/// third\nvoid F() {}\n", 3, 1, 3, 1, 0, 0)]
    [InlineData("int x = 1; // trailing - with a dash\n", 0, 1, 0, 0, 1, 0)]
    [InlineData("// a spaced double dash -- counts too\n", 1, 0, 1, 0, 1, 0)]
    [InlineData("// chosen deliberately, by design\n", 1, 0, 1, 0, 0, 2)]
    [InlineData("// at 0x14028CC0: see Offsets.cs:12 and 13:45\n", 1, 0, 1, 0, 0, 0)]
    [InlineData("///   - a bullet item\n/// says \"a: b\" in a string and `x: y` in code\n", 2, 0, 2, 0, 0, 0)]
    public void Measure_counts_what_the_rules_read(string text, int lines, int code, int block, int colons, int dashes, int tells)
    {
        var m = MeasureText(text);
        Assert.Equal((lines, code, block, colons, dashes, tells), (m.CommentLines, m.CodeLines, m.MaxBlock, m.Colons, m.Dashes, m.Tells.Count));
    }

    [Fact]
    public void No_comment_carries_a_tell_phrase_a_colon_or_a_dash()
    {
        var hits = Current().Where(kv => kv.Value.Tells.Count > 0 || kv.Value.Colons > 0 || kv.Value.Dashes > 0)
            .Select(kv => $"  {kv.Key}, {kv.Value.Colons} colons, {kv.Value.Dashes} dashes, tells {string.Join(", ", kv.Value.Tells)}").ToList();
        Assert.True(hits.Count == 0, "comments that argue, or carry a colon or dash inside a sentence (the owner writes neither):\n" + string.Join("\n", hits));
    }

    [Fact]
    public void Comment_budget_holds_against_the_frozen_baseline()
    {
        var baseline = LoadBaseline();
        var current = Current();
        var problems = new List<string>();
        var rows = new List<string>();
        foreach (var (key, m) in current.OrderBy(kv => kv.Key, StringComparer.Ordinal))
        {
            string row = $"  \"{key}\": [{m.CommentLines}, {m.MaxBlock}],";
            if (baseline.TryGetValue(key, out var b))
            {
                int allowed = b[0] + Math.Max(GrowthFloor, (int)Math.Ceiling(b[0] * GrowthAllowance));
                if (m.CommentLines > allowed) problems.Add($"{key} has {m.CommentLines} comment lines, baseline {b[0]} allows {allowed}");
                if (m.MaxBlock > b[1]) problems.Add($"{key} has a comment block of {m.MaxBlock} lines, baseline {b[1]}");
                if (m.CommentLines < b[0] || m.MaxBlock < b[1]) rows.Add(row + "   shrank, paste to tighten");
            }
            else
            {
                double ratio = m.CodeLines == 0 ? 0 : (double)m.CommentLines / m.CodeLines;
                if (ratio > NewFileMaxRatio) problems.Add($"{key} (new) has {m.CommentLines} comment lines over {m.CodeLines} code lines, cap is one in three");
                if (m.MaxBlock > NewFileMaxBlock) problems.Add($"{key} (new) has a comment block of {m.MaxBlock} lines, cap is {NewFileMaxBlock}");
                rows.Add(row + "   new file, paste to freeze");
            }
        }
        foreach (var key in baseline.Keys.Except(current.Keys)) rows.Add($"  {key} no longer exists, drop its row");
        Assert.True(problems.Count == 0,
            "Comment budget exceeded.\n\n" + string.Join("\n", problems) +
            "\n\nIf the growth is earned, the owner raises the row in comments.json; otherwise cut the comment.\n" +
            (rows.Count == 0 ? "" : "\nRows that moved (paste into comments.json):\n" + string.Join("\n", rows)));
    }

    /// <summary>The first sentence of the first summary block, whitespace collapsed, or null when the file has none.</summary>
    internal static string? FirstSummarySentence(string fileText)
    {
        var m = Regex.Match(fileText, @"///\s*<summary>(.*?)</summary>", RegexOptions.Singleline);
        if (!m.Success) return null;
        string text = Regex.Replace(Regex.Replace(m.Groups[1].Value, @"\s*///\s*", " "), @"\s+", " ").Trim();
        return Regex.Split(text, @"(?<=[.!?])\s", RegexOptions.None)[0];
    }

    private static bool IsShortSentence(string sentence) => sentence.Length <= MaxFirstSentence && sentence.EndsWith('.');

    [Theory]
    [InlineData("/// <summary>Counts kills.</summary>", "Counts kills.", true)]
    [InlineData("/// <summary>Counts kills. More detail follows.</summary>", "Counts kills.", true)]
    [InlineData("/// <summary>Counts kills</summary>", "Counts kills", false)]
    [InlineData("/// <summary>Opens the door, e.g. the front one. Then more.</summary>", "Opens the door, e.g.", true)]
    [InlineData("/// <summary>Reads <see cref=\"X\"/> now.</summary>", "Reads <see cref=\"X\"/> now.", true)]
    [InlineData("/// <summary>\n/// Counts\n///   the kills.\n/// </summary>", "Counts the kills.", true)]
    [InlineData("class C { }", null, false)]
    public void First_summary_sentence_follows_the_definition(string fileText, string? expected, bool passes)
    {
        string? got = FirstSummarySentence(fileText);
        Assert.Equal(expected, got);
        if (got is not null) Assert.Equal(passes, IsShortSentence(got));
    }

    [Fact]
    public void First_summary_sentence_of_exactly_110_characters_passes_and_111_fails()
    {
        string at110 = new string('a', 109) + ".";
        Assert.True(IsShortSentence(FirstSummarySentence($"/// <summary>{at110}</summary>")!));
        Assert.False(IsShortSentence(FirstSummarySentence($"/// <summary>a{at110}</summary>")!));
    }

    [Fact]
    public void Every_production_file_opens_with_a_short_first_sentence()
    {
        var exempt = Rules.Load().NoSummaryExempt;
        var bad = new List<string>();
        foreach (var (key, path) in ProductionFiles())
        {
            string? first = FirstSummarySentence(File.ReadAllText(path));
            if (first is null)
            {
                if (!exempt.ContainsKey(Path.GetFileName(path))) bad.Add($"{key} (no summary block)");
            }
            else if (!IsShortSentence(first)) bad.Add($"{key} ({first.Length} chars) {first}");
        }
        Assert.True(bad.Count == 0, $"{bad.Count} files need a first summary sentence of at most {MaxFirstSentence} characters ending in a period.\n" + string.Join("\n", bad));
    }

    [Fact]
    public void AssemblyInfo_opens_with_a_one_line_comment()
    {
        string path = Path.Combine(Rules.Load().ProdDir, "AssemblyInfo.cs");
        if (!File.Exists(path)) return;
        string first = File.ReadAllLines(path).Select(l => l.Trim()).First(l => l.Length > 0 && !l.StartsWith("using "));
        Assert.True(first.StartsWith("// ") && first.Length <= MaxFirstSentence, $"AssemblyInfo.cs must open with a one line comment of at most {MaxFirstSentence} characters, found {first}");
    }

    [Fact]
    public void Every_summary_exemption_names_a_real_production_file()
    {
        var names = ProductionFiles().Select(p => Path.GetFileName(p.FullPath)).ToHashSet(StringComparer.Ordinal);
        var stale = Rules.Load().NoSummaryExempt.Keys.Where(k => !names.Contains(k)).ToList();
        Assert.True(stale.Count == 0, "Stale exemptions " + string.Join(", ", stale));
    }
}
