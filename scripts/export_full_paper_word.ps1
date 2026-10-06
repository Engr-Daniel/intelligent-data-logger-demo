param(
    [string]$DocumentPath = (Join-Path $PSScriptRoot '../paper/submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave.docx'),
    [string]$PdfPath = (Join-Path $PSScriptRoot '../paper/submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave.pdf')
)
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$initialDocuments = $word.Documents.Count
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
$document = $null
try {
    $path = $DocumentPath
    $document = $word.Documents.Open($path, $false, $false)
    $document.Fields.Update() | Out-Null
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    $document.Repaginate()
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    $document.Save()
    $document.ExportAsFixedFormat($PdfPath,17)
    Write-Output ('Word pages: ' + $document.ComputeStatistics(2))
    Write-Output ('Contents/list fields: ' + $document.TablesOfContents.Count)
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($initialDocuments -eq 0) { $word.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
