// Test Range Box: logic thuần (BRAINSTORM mục 7) + đối chiếu Python↔C# + render PNG.
// Chạy: dotnet run --project quantower-range/tests
using System;
using System.Collections.Generic;
using System.IO;
using RangeBox;

static partial class T
{
    static int _ok, _fail;

    public static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (ok) _ok++; else _fail++;
    }

    /// <summary>Thư mục quantower-range (đi ngược từ thư mục chạy tới khi thấy RangeLogic.cs).</summary>
    public static string Root()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d != null && !File.Exists(Path.Combine(d.FullName, "RangeLogic.cs"))) d = d.Parent;
        return d?.FullName ?? Directory.GetCurrentDirectory();
    }

    static int Main()
    {
        LogicTests.RunAll();
        UiTests.RunAll();
        AdversarialTests.RunAll();
        Console.WriteLine();
        Console.WriteLine(_fail == 0 ? $"=== PASS: {_ok} OK, 0 FAIL ===" : $"=== {_fail} FAIL, {_ok} OK ===");
        return _fail;
    }
}
