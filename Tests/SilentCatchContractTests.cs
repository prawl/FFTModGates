using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;

namespace ModGates.Tests;

/// <summary>
/// Holds the empty catch count at zero. A file still carrying some on the day the rules arrive
/// lists its count in rules.json, and that count may only go down. The regex is the one
/// health.py counts with, so a catch holding only a comment still counts.
/// </summary>
public class SilentCatchContractTests
{
    private static readonly Regex EmptyCatch = new(@"catch(\s*\([^)]*\))?(\s*when\s*\([^)]*\))?\s*\{\s*(/\*[^*]*\*/)?\s*\}", RegexOptions.Compiled);

    private static Dictionary<string, int> CountsPerFile()
    {
        var counts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        string root = Rules.Load().ProdDir;
        foreach (var file in Directory.GetFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            string rel = Path.GetRelativePath(root, file).Replace('\\', '/');
            if (rel.StartsWith("bin/") || rel.StartsWith("obj/")) continue;
            int n = EmptyCatch.Matches(File.ReadAllText(file)).Count;
            if (n > 0) counts[rel] = n;
        }
        return counts;
    }

    [Fact]
    public void No_production_file_has_an_empty_catch()
    {
        var allowed = Rules.Load().SilentCatchAllowlist;
        var counts = CountsPerFile();
        var over = counts.Where(kv => kv.Value > allowed.GetValueOrDefault(kv.Key)).Select(kv => $"{kv.Key}: {kv.Value} (allowed {allowed.GetValueOrDefault(kv.Key)})").ToList();
        Assert.True(over.Count == 0, "Empty catches found (note the fault or log it, never swallow it):\n" + string.Join("\n", over));
    }

    [Fact]
    public void The_silent_catch_allowlist_only_shrinks_and_names_real_files()
    {
        var allowed = Rules.Load().SilentCatchAllowlist;
        var counts = CountsPerFile();
        var stale = allowed.Where(kv => counts.GetValueOrDefault(kv.Key) < kv.Value)
            .Select(kv => $"{kv.Key}: allows {kv.Value}, has {counts.GetValueOrDefault(kv.Key)}; lower the entry or drop it").ToList();
        Assert.True(stale.Count == 0, "A fixed catch must tighten silentCatchAllowlist in the same change:\n" + string.Join("\n", stale));
    }
}
