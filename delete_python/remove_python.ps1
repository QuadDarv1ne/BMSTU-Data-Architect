<#
.SYNOPSIS
Полное удаление Python и очистка VSCode
.DESCRIPTION
Удаляет все версии Python, очищает кэш VSCode и системные настройки
#>

# Проверка прав администратора
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Restarting with admin rights..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "=== PYTHON AND VSCODE CLEANER ===" -ForegroundColor Cyan

# 1. УДАЛЕНИЕ УСТАНОВЛЕННЫХ ВЕРСИЙ PYTHON
Write-Host "`n[1/4] Searching Python installations..." -ForegroundColor Yellow
$pythonInstallations = Get-ChildItem -Path @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
) | ForEach-Object { 
    Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
} | Where-Object { 
    $_.DisplayName -match "Python [0-9]+|Anaconda"
} | Select-Object DisplayName, UninstallString

if (-not $pythonInstallations) {
    Write-Host "No Python installations found" -ForegroundColor Green
}
else {
    foreach ($install in $pythonInstallations) {
        if ($install.UninstallString) {
            $uninstallString = $install.UninstallString.Trim()
            
            if ($uninstallString -match "msiexec") {
                # MSI installer
                $uninstallPath = $uninstallString -replace ".*(\\|\/)", "" -replace "[""']", ""
                Write-Host "Uninstalling: $($install.DisplayName)" -ForegroundColor Red
                Start-Process "msiexec.exe" -ArgumentList "/X $uninstallPath /qn /norestart" -Wait
            }
            else {
                # EXE installer
                Write-Host "Uninstalling: $($install.DisplayName)" -ForegroundColor Red
                Start-Process -FilePath $uninstallString -ArgumentList "/S" -Wait
            }
        }
    }
}

# 2. УДАЛЕНИЕ ОСТАТОЧНЫХ ФАЙЛОВ
Write-Host "`n[2/4] Removing Python files..." -ForegroundColor Yellow
$pythonPaths = @(
    "${env:ProgramFiles}\Python*",
    "${env:LocalAppData}\Programs\Python*",
    "${env:AppData}\Python",
    "${env:UserProfile}\AppData\Local\Programs\Python",
    "${env:UserProfile}\AppData\Local\pip",
    "${env:UserProfile}\.python",
    "${env:UserProfile}\.conda"
)

$totalRemoved = 0
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        Write-Host "Deleting: $path" -ForegroundColor Magenta
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        $totalRemoved++
    }
}
Write-Host "Folders removed: $totalRemoved" -ForegroundColor Green

# 3. ОЧИСТКА VSCODE
Write-Host "`n[3/4] Cleaning VSCode..." -ForegroundColor Yellow
$vscodePaths = @(
    "$env:APPDATA\Code\User\globalStorage\ms-python.python",
    "$env:APPDATA\Code\Cache",
    "$env:APPDATA\Code\CachedData",
    "$env:APPDATA\Code\CachedExtensions"
)

foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        Write-Host "Cleaning: $path" -ForegroundColor Blue
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Очистка settings.json
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    try {
        $content = Get-Content $settingsPath -Raw
        $json = $content | ConvertFrom-Json
        
        # Удаление Python-настроек
        $properties = $json.PSObject.Properties | 
            Where-Object { $_.Name -notmatch "^python\.|^conda\.|^jupyter\." }
        
        $newConfig = New-Object PSObject
        foreach ($prop in $properties) {
            $newConfig | Add-Member -MemberType NoteProperty -Name $prop.Name -Value $prop.Value
        }
        
        $newConfig | ConvertTo-Json | Set-Content $settingsPath
        Write-Host "VSCode settings cleaned" -ForegroundColor Blue
    }
    catch {
        Write-Host "Error processing settings.json" -ForegroundColor Red
    }
}

# Удаление расширения
try {
    & code --uninstall-extension ms-python.python --force 2>$null
    Write-Host "Python extension uninstalled" -ForegroundColor Green
}
catch {
    Write-Host "Failed to remove Python extension" -ForegroundColor Red
}

# 4. ОЧИСТКА СИСТЕМНЫХ НАСТРОЕК
Write-Host "`n[4/4] Cleaning system..." -ForegroundColor Yellow

# Переменные среды
$envVars = @("PYTHONPATH", "PYTHONHOME", "ANACONDA_HOME")
foreach ($var in $envVars) {
    [Environment]::SetEnvironmentVariable($var, $null, "User")
    [Environment]::SetEnvironmentVariable($var, $null, "Machine")
    Write-Host "Removed variable: $var" -ForegroundColor DarkGray
}

# Виртуальные окружения
$venvPaths = @(
    "$env:UserProfile\venv",
    "$env:UserProfile\.virtualenvs",
    "$PWD\venv",
    "$PWD\.venv"
)

foreach ($path in $venvPaths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed virtualenv: $path" -ForegroundColor DarkGray
    }
}

# ФИНАЛЬНЫЙ ОТЧЕТ
Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Recommendations:" -ForegroundColor Yellow
Write-Host "1. Reboot your computer"
Write-Host "2. Check installed programs for Python"
Write-Host "3. Reinstall Python extension in VSCode if needed"

# Заметки для пользователя:
<#
РУССКИЕ ЗАМЕТКИ ДЛЯ ПОЛЬЗОВАТЕЛЯ:

1. Этот скрипт полностью удаляет:
   - Все установленные версии Python
   - Anaconda и связанные компоненты
   - Кэш и настройки VSCode для Python
   - Системные переменные окружения

2. После выполнения:
   - Проверьте "Программы и компоненты" на наличие остатков Python
   - Удалите вручную оставшиеся папки Python, если найдете
   - В VSCode проверьте отсутствие интерпретаторов Python

3. Для повторной установки:
   - Скачайте Python с официального сайта
   - Перезагрузите компьютер перед установкой
   - Установите расширение Python для VSCode заново

4. Особенности работы:
   - Требует прав администратора
   - Автоматически перезапускается с правами админа
   - Не удаляет пользовательские скрипты и проекты
   - Сохраняет другие настройки VSCode
#>
