using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;
int bad = 0;
int max = int.TryParse(Environment.GetEnvironmentVariable("OXV_MAX"), out var mm) ? mm : 25;
foreach (var path in args) {
  try {
    OpenXmlPackage pkg = path.EndsWith(".pptx") ? PresentationDocument.Open(path, false)
                      : path.EndsWith(".docx") ? WordprocessingDocument.Open(path, false)
                      : SpreadsheetDocument.Open(path, false);
    using (pkg) {
      var v = new OpenXmlValidator(Enum.Parse<FileFormatVersions>(Environment.GetEnvironmentVariable("OXV_VER") ?? "Microsoft365"));
      var errs = v.Validate(pkg).ToList();
      Console.WriteLine($"== {System.IO.Path.GetFileName(path)}: {errs.Count} errors");
      foreach (var e in errs.Take(max))
        Console.WriteLine($"  [{e.ErrorType}] {e.Part?.Uri} {e.Path?.XPath}\n     {e.Description}");
      bad += errs.Count;
    }
  } catch (Exception ex) { Console.WriteLine($"== {path}: OPEN FAILED {ex.GetType().Name}: {ex.Message}"); bad++; }
}
return bad > 0 ? 1 : 0;
