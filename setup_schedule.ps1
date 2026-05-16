# 创建 Windows 定时任务：每天早上 9:00 运行资源推送
# 右键此文件 → "使用 PowerShell 运行"（需要管理员权限）

$taskName = "AutoResourcePusher"
$scriptPath = Join-Path $PSScriptRoot "run.bat"

$action = New-ScheduledTaskAction -Execute $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "每天自动推送优质资源到飞书"

Write-Host "定时任务已创建：每天早上 9:00 运行"
Write-Host "可在 '任务计划程序' (taskschd.msc) 中查看和管理"
