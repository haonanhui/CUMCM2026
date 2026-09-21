# Dot-source from PowerShell: . ./Enter-Workspace.ps1
# Session-only PATH setup. No global environment or Harness config is changed.
$nativeWorkspaceRoot = $PSScriptRoot
Set-Location -LiteralPath $nativeWorkspaceRoot
$nativePythonBin = Join-Path $nativeWorkspaceRoot '.venv/Scripts'
if (Test-Path -LiteralPath $nativePythonBin) { $env:PATH = "$nativePythonBin;$env:PATH" }
$nativeToolchainFile = Join-Path $nativeWorkspaceRoot '.local/toolchain.json'
if (Test-Path -LiteralPath $nativeToolchainFile) {
    $nativeToolchain = Get-Content -LiteralPath $nativeToolchainFile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($nativeToolchain.tex_bin -and (Test-Path -LiteralPath $nativeToolchain.tex_bin)) {
        $env:PATH = "$($nativeToolchain.tex_bin);$env:PATH"
    }
}
$env:PYTHONDONTWRITEBYTECODE = '1'
Write-Host "Workspace: $nativeWorkspaceRoot"
Write-Host 'Run codex or dsh --profile tui using your existing login/profile.'
