# Pytuitor learner shell; your own profile is not read or modified.
$e = [char]27
function prompt {
  $folder = Split-Path -Leaf (Get-Location)
  "$e[34m{{PY}} $e[33m$env:PYTUITOR_LABEL$e[0m $e[36m{{FOLDER}}  $folder$e[0m ❯ "
}
Write-Host ""
Write-Host "  {{PY}}  Pytuitor  ·  $env:PYTUITOR_TITLE  ·  $env:PYTUITOR_STAGE" -ForegroundColor Blue
Write-Host "  This terminal runs in your $env:PYTUITOR_STAGE workspace on this computer." -ForegroundColor DarkGray
Write-Host "  Type $env:PYTUITOR_RUN or press Run to try your program." -ForegroundColor DarkGray
Write-Host ""
