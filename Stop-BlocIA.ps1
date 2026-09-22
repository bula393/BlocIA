param()
$ErrorActionPreference = 'Stop'
$processFile = Join-Path $PSScriptRoot 'back/data/run/processes.json'
if (!(Test-Path -LiteralPath $processFile)) { exit 0 }
$savedProcesses = Get-Content -LiteralPath $processFile -Raw | ConvertFrom-Json
foreach ($saved in $savedProcesses) {
    $ownedProcess = Get-Process -Id $saved.id -ErrorAction SilentlyContinue
    if ($ownedProcess -and $ownedProcess.StartTime.ToUniversalTime().ToString('O') -eq $saved.startedAt) {
        # The virtual-environment launcher can spawn a separate Python process.
        # Stop the whole owned process tree so the server releases its port.
        & taskkill.exe /PID $ownedProcess.Id /T /F | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo detener el proceso de $($saved.name)."
        }
    }
}
Write-Output 'Se detuvieron los procesos iniciados por Start-BlocIA.ps1.'
