# install.ps1 - installs env-watcher on Windows via Task Scheduler
# Run as Administrator for best results.

$BUS_DIR = Join-Path $env:USERPROFILE "Desktop\IDE\.agents\bus"
$PYTHON  = "python"

if (-not (Get-Command $PYTHON -ErrorAction SilentlyContinue)) {
    $PYTHON = "C:\Python314\python.exe"
}

Write-Host "[install] Installing dependencies..."
& $PYTHON -m pip install mcp watchdog --quiet

Write-Host "[install] Registering Task Scheduler task..."
$action   = New-ScheduledTaskAction -Execute $PYTHON -Argument "`"$BUS_DIR\watcher.py`" --daemon"
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "AntigravityEnvWatcher" `
    -TaskPath "\AntigravityIDE\" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Force | Out-Null

Write-Host "[install] Starting watcher now..."
Start-ScheduledTask -TaskPath "\AntigravityIDE\" -TaskName "AntigravityEnvWatcher"
Write-Host "[install] Done. env-watcher is active and will auto-start on every login."
