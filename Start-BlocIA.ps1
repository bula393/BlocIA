param()
$ErrorActionPreference = 'Stop'
$workspaceRoot = $PSScriptRoot
$runtimeDirectory = Join-Path $workspaceRoot 'back/data/run'
$processFile = Join-Path $runtimeDirectory 'processes.json'
New-Item -ItemType Directory -Force -Path $runtimeDirectory | Out-Null
if (Test-Path -LiteralPath $processFile) {
    $savedProcesses = Get-Content -LiteralPath $processFile -Raw | ConvertFrom-Json
    $stillRunning = @($savedProcesses | Where-Object {
        $savedProcess = Get-Process -Id $_.id -ErrorAction SilentlyContinue
        $savedProcess -and $savedProcess.StartTime.ToUniversalTime().ToString('O') -eq $_.startedAt
    })
    if ($stillRunning.Count -gt 0) {
        Write-Output 'BlocIA ya tiene procesos activos. Abrí http://127.0.0.1:5173 o ejecutá Stop-BlocIA.ps1 antes de reiniciar.'
        exit 0
    }
}
$pythonPath = Join-Path $workspaceRoot 'back/.venv/Scripts/python.exe'
$vitePath = Join-Path $workspaceRoot 'front/node_modules/vite/bin/vite.js'
$nodePath = (Get-Command node.exe -ErrorAction Stop).Source
foreach ($servicePort in @(8000, 5173)) {
    $portProbe = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $servicePort)
    try { $portProbe.Start() }
    catch { throw "El puerto $servicePort está ocupado. Cerrá la instancia anterior antes de iniciar BlocIA." }
    finally { $portProbe.Stop() }
}
if (!(Test-Path -LiteralPath $pythonPath) -or !(Test-Path -LiteralPath $vitePath)) {
    throw 'Faltan dependencias. Consultá README.md para instalar el proyecto.'
}
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $workspaceRoot 'back') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDirectory 'backend.out.log') -RedirectStandardError (Join-Path $runtimeDirectory 'backend.err.log') -PassThru
$frontendProcess = Start-Process -FilePath $nodePath -ArgumentList @(('"' + $vitePath + '"'), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WorkingDirectory (Join-Path $workspaceRoot 'front') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDirectory 'frontend.out.log') -RedirectStandardError (Join-Path $runtimeDirectory 'frontend.err.log') -PassThru
@(
    @{ name = 'backend'; id = $backendProcess.Id; startedAt = $backendProcess.StartTime.ToUniversalTime().ToString('O') },
    @{ name = 'frontend'; id = $frontendProcess.Id; startedAt = $frontendProcess.StartTime.ToUniversalTime().ToString('O') }
) | ConvertTo-Json | Set-Content -LiteralPath $processFile -Encoding utf8
Write-Output 'BlocIA: http://127.0.0.1:5173/nuevo-chat'
Write-Output 'Estado de la base: http://127.0.0.1:8000/health'
Write-Output 'Los registros de ejecución están en back/data/run.'
