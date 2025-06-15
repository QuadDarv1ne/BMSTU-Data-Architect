#Requires -Version 5.1
<#
.СИНОПСИС
Полное удаление всех интерпретаторов Python и связанных настроек VSCode

.ОПИСАНИЕ
Этот скрипт выполняет:
1. Удаление всех установленных версий Python через установщик Windows
2. Очистку остаточных файлов Python
3. Удаление настроек VSCode, зависящих от Python
4. Очистку переменных окружения Python
5. Удаление виртуальных окружений и кэша

.ТРЕБОВАНИЯ
- Запуск от имени администратора
- Windows PowerShell 5.1+
- VSCode (опционально)

.ПРИМЕЧАНИЯ
Версия: 1.4
Автор: Claude
Дата: 2024
#>

param (
    [switch]$Force = $false,        # Принудительное выполнение без подтверждений
    [switch]$Backup = $false,       # Создание резервной копии настроек VSCode
    [switch]$LogToFile = $false,    # Запись лога в файл
    [string]$LogPath = "$env:USERPROFILE\Desktop\python_cleanup.log",  # Путь к файлу лога
    [ValidateSet('en', 'ru')]
    [string]$Language = 'en'        # Язык интерфейса (en/ru)
)

# Строки локализации
$strings = @{
    en = @{
        StartingCleanup = "=== STARTING PYTHON AND VSCODE CLEANUP ==="
        RunningProcesses = "Running processes detected"
        ContinueRemoval = "Do you want to continue removal?"
        Yes = "Yes"
        No = "No"
        All = "All"
        Cancel = "Cancel"
        ImportantProjects = "Important projects detected"
        NoPythonFound = "No installed Python versions found"
        FoundVersions = "Found installed versions: {0}"
        RemovePython = "Remove Python"
        RemoveVersion = "Remove {0}?`nPath: {1}"
        RemoveThisVersion = "Remove this version"
        SkipThisVersion = "Skip this version"
        RemoveAllNoConfirm = "Remove all without confirmation"
        AbortScript = "Abort script execution"
        RemovingMSI = "Removing MSI: {0} [{1}]"
        RemovingEXE = "Removing EXE: {0}"
        SuccessfullyRemoved = "Successfully removed: {0}"
        RemovalError = "Removal error (code {0}): {1}"
        ErrorRemoving = "Error removing {0}: {1}"
        RemovingResidual = "`n[2/5] Removing residual Python files..."
        PythonFolder = "Python folder"
        CleaningVSCode = "`n[3/5] Cleaning VSCode settings..."
        VSCodeFolder = "VSCode folder"
        RemovingPythonExt = "Removing Python extension for VSCode..."
        PythonExtRemoved = "Python extension for VSCode removed"
        VSCodeNotFound = "VSCode not found in PATH, skipping extension removal"
        ErrorRemovingExt = "Error removing VSCode extension: {0}"
        CleaningEnvVars = "`n[4/5] Cleaning environment variables..."
        RemovedVariable = "Removed variable: {0}"
        RemovingVenvs = "`n[5/5] Removing virtual environments..."
        VirtualEnv = "virtual environment"
        CleanupCompleted = "=== CLEANUP COMPLETED ==="
        Results = "Results:"
        RemovedVersions = " - Removed Python versions: {0}"
        RemovedFolders = " - Removed folders: {0}"
        CleanedVSCode = " - Cleaned VSCode items: {0}"
        RemovedEnvVars = " - Removed environment variables: {0}"
        RemovedVenvs = " - Removed virtual environments: {0}"
        Recommendations = "`nRecommendations:"
        RestartPC = "1. Restart your computer"
        CheckPrograms = "2. Check Programs and Features for any remaining Python installations"
        CheckEnvVars = "3. Check environment variables in system settings"
        ReinstallIfNeeded = "4. Reinstall Python and VSCode extensions if needed"
        PressAnyKey = "`nPress any key to exit..."
    }
    ru = @{
        StartingCleanup = "=== НАЧАЛО ОЧИСТКИ PYTHON И VSCODE ==="
        RunningProcesses = "Обнаружены запущенные процессы"
        ContinueRemoval = "Хотите продолжить удаление?"
        Yes = "Да"
        No = "Нет"
        All = "Все"
        Cancel = "Отмена"
        ImportantProjects = "Обнаружены важные проекты"
        NoPythonFound = "Установленные версии Python не найдены"
        FoundVersions = "Найдено установленных версий: {0}"
        RemovePython = "Удаление Python"
        RemoveVersion = "Удалить {0}?`nПуть: {1}"
        RemoveThisVersion = "Удалить эту версию"
        SkipThisVersion = "Пропустить эту версию"
        RemoveAllNoConfirm = "Удалить все без подтверждения"
        AbortScript = "Прервать выполнение скрипта"
        RemovingMSI = "Удаление MSI: {0} [{1}]"
        RemovingEXE = "Удаление EXE: {0}"
        SuccessfullyRemoved = "Успешно удалено: {0}"
        RemovalError = "Ошибка удаления (код {0}): {1}"
        ErrorRemoving = "Ошибка при удалении {0}: {1}"
        RemovingResidual = "`n[2/5] Удаление остаточных файлов Python..."
        PythonFolder = "папка Python"
        CleaningVSCode = "`n[3/5] Очистка настроек VSCode..."
        VSCodeFolder = "папка VSCode"
        RemovingPythonExt = "Удаление расширения Python для VSCode..."
        PythonExtRemoved = "Расширение Python для VSCode удалено"
        VSCodeNotFound = "VSCode не найден в PATH, пропуск удаления расширения"
        ErrorRemovingExt = "Ошибка удаления расширения VSCode: {0}"
        CleaningEnvVars = "`n[4/5] Очистка переменных окружения..."
        RemovedVariable = "Удалена переменная: {0}"
        RemovingVenvs = "`n[5/5] Удаление виртуальных окружений..."
        VirtualEnv = "виртуальное окружение"
        CleanupCompleted = "=== ОЧИСТКА ЗАВЕРШЕНА ==="
        Results = "Результаты:"
        RemovedVersions = " - Удалено версий Python: {0}"
        RemovedFolders = " - Удалено папок: {0}"
        CleanedVSCode = " - Очищено элементов VSCode: {0}"
        RemovedEnvVars = " - Удалено переменных окружения: {0}"
        RemovedVenvs = " - Удалено виртуальных окружений: {0}"
        Recommendations = "`nРекомендации:"
        RestartPC = "1. Перезагрузите компьютер"
        CheckPrograms = "2. Проверьте Программы и компоненты на наличие оставшихся установок Python"
        CheckEnvVars = "3. Проверьте переменные окружения в системных настройках"
        ReinstallIfNeeded = "4. Переустановите Python и расширения VSCode при необходимости"
        PressAnyKey = "`nНажмите любую клавишу для выхода..."
    }
}

# Функция для получения локализованной строки
function Get-LocalizedString {
    param (
        [string]$Key,               # Ключ строки
        [object[]]$FormatArgs = @() # Аргументы форматирования
    )
    $string = $strings[$Language][$Key]
    if ($FormatArgs.Count -gt 0) {
        $string = [string]::Format($string, $FormatArgs)
    }
    return $string
}

# Функция для записи лога
function Write-Log {
    param (
        [string]$Message,           # Сообщение для записи в лог
        [string]$Level = "INFO"     # Уровень сообщения
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    if ($LogToFile) {
        Add-Content -Path $LogPath -Value $logMessage
    }
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    
    Write-Host $logMessage -ForegroundColor $color
}

# Функция для создания резервной копии настроек VSCode
function Backup-VSCodeSettings {
    param (
        [string]$BackupPath = "$env:USERPROFILE\Desktop\vscode_backup"  # Путь для резервной копии
    )
    try {
        if (-not (Test-Path $BackupPath)) {
            New-Item -ItemType Directory -Path $BackupPath | Out-Null
        }
        
        $vscodePaths = @(
            "${env:APPDATA}\Code\User\settings.json",
            "${env:APPDATA}\Code\User\keybindings.json",
            "${env:APPDATA}\Code\User\snippets"
        )
        
        foreach ($path in $vscodePaths) {
            if (Test-Path $path) {
                Copy-Item -Path $path -Destination $BackupPath -Recurse -Force
                Write-Log "Backup created: $path" -Level "SUCCESS"
            }
        }
        return $true
    }
    catch {
        Write-Log "Error creating backup: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Функция проверки запущенных процессов Python
function Test-RunningPythonProcesses {
    $pythonProcesses = Get-Process | Where-Object { $_.ProcessName -match "python|jupyter|ipython" }
    if ($pythonProcesses) {
        Write-Log "Found running Python processes:" -Level "WARNING"
        $pythonProcesses | ForEach-Object {
            Write-Log "  - $($_.ProcessName) (PID: $($_.Id))" -Level "WARNING"
        }
        return $true
    }
    return $false
}

# Функция проверки важных проектов Python
function Test-ImportantPythonProjects {
    $importantPaths = @(
        "$env:USERPROFILE\Documents\Python",
        "$env:USERPROFILE\Projects",
        "$env:USERPROFILE\Desktop\Python"
    )
    
    $foundProjects = @()
    foreach ($path in $importantPaths) {
        if (Test-Path $path) {
            $pythonFiles = Get-ChildItem -Path $path -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
            if ($pythonFiles) {
                $foundProjects += $path
            }
        }
    }
    
    if ($foundProjects) {
        Write-Log "Found potentially important Python projects:" -Level "WARNING"
        $foundProjects | ForEach-Object {
            Write-Log "  - $_" -Level "WARNING"
        }
        return $true
    }
    return $false
}

# Функция очистки PATH от зависимостей Python
function Clear-PythonFromPath {
    try {
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        $machinePath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        $pythonPaths = @(
            "Python",
            "Anaconda",
            "Miniconda",
            "Scripts"
        )
        
        $newUserPath = ($userPath -split ';' | Where-Object { 
            -not ($pythonPaths | Where-Object { $path -match $_ })
        }) -join ';'
        
        $newMachinePath = ($machinePath -split ';' | Where-Object { 
            -not ($pythonPaths | Where-Object { $path -match $_ })
        }) -join ';'
        
        [Environment]::SetEnvironmentVariable("PATH", $newUserPath, "User")
        [Environment]::SetEnvironmentVariable("PATH", $newMachinePath, "Machine")
        
        Write-Log "PATH cleaned from Python-dependent paths" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error cleaning PATH: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Проверка версии PowerShell
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Error "PowerShell version 5.1 or higher is required"
    exit 1
}

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Restarting script with administrator rights..." -ForegroundColor Yellow
    try {
        $processArgs = @{
            FilePath = 'powershell.exe'
            ArgumentList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Force"
            Verb = 'RunAs'
            Wait = $true
        }
        Start-Process @processArgs
    }
    catch {
        Write-Error "Failed to run script with administrator rights. Please run PowerShell as administrator and try again."
    }
    exit
}

# Функция безпасного удаления файла/папки
function Remove-Safe {
    param (
        [string]$Path,              # Путь к удаляемому файлу/папке
        [string]$Description        # Описание удаляемого объекта
    )
    try {
        if (Test-Path $Path) {
            Write-Host ("Removing " + $Description + ": " + $Path) -ForegroundColor Magenta
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            return $true
        }
        return $false
    }
    catch {
        Write-Host ("Error removing " + $Description + ": " + $_.Exception.Message) -ForegroundColor Red
        return $false
    }
}

# Функция очистки настроек VSCode
function Clean-VSCodeSettings {
    param (
        [string]$Path               # Путь к файлу настроек
    )
    try {
        if (-not (Test-Path $Path)) { return $false }
        
        $content = Get-Content $Path -Raw -ErrorAction Stop
        
        # Проверка на пустой файл
        if ([string]::IsNullOrWhiteSpace($content)) {
            Write-Host "Settings file is empty: $Path" -ForegroundColor Yellow
            return $false
        }
        
        $json = $content | ConvertFrom-Json -ErrorAction Stop
        
        # Получение списка свойств, связанных с Python
        $pythonProps = $json.PSObject.Properties | 
            Where-Object { $_.Name -match "^python\.|^conda\.|^jupyter\." } |
            Select-Object -ExpandProperty Name
        
        if (-not $pythonProps) {
            Write-Host "No Python settings found: $Path" -ForegroundColor Green
            return $false
        }
        
        # Создание нового объекта конфигурации без свойств Python
        $newConfig = New-Object PSObject
        $json.PSObject.Properties | 
            Where-Object { $_.Name -notin $pythonProps } |
            ForEach-Object {
                $newConfig | Add-Member -MemberType NoteProperty -Name $_.Name -Value $_.Value
            }
        
        # Сохранение только при изменении
        $newJson = $newConfig | ConvertTo-Json
        if ($newJson -ne $content) {
            $newJson | Set-Content $Path -Force
            Write-Host "Cleaned Python settings: $($pythonProps.Count) in $Path" -ForegroundColor Blue
            return $true
        }
        
        Write-Host "No changes needed: $Path" -ForegroundColor Green
        return $false
    }
    catch {
        Write-Host ("Error processing VSCode settings: " + $_.Exception.Message) -ForegroundColor Red
        return $false
    }
}

# Основной процесс очистки
Write-Log (Get-LocalizedString "StartingCleanup") -Level "INFO"

# Проверка запущенных процессов
if (Test-RunningPythonProcesses) {
    if (-not $Force) {
        $title = Get-LocalizedString "RunningProcesses"
        $question = Get-LocalizedString "ContinueRemoval"
        $choices = @(
            [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "Yes"), (Get-LocalizedString "RemoveThisVersion"))
            [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "No"), (Get-LocalizedString "SkipThisVersion"))
        )
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
        if ($decision -eq 1) { exit }
    }
}

# Проверка важных проектов
if (Test-ImportantPythonProjects) {
    if (-not $Force) {
        $title = Get-LocalizedString "ImportantProjects"
        $question = Get-LocalizedString "ContinueRemoval"
        $choices = @(
            [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "Yes"), (Get-LocalizedString "RemoveThisVersion"))
            [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "No"), (Get-LocalizedString "SkipThisVersion"))
        )
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
        if ($decision -eq 1) { exit }
    }
}

# Создание резервной копии настроек VSCode при необходимости
if ($Backup) {
    if (Backup-VSCodeSettings) {
        Write-Log "VSCode settings backup created successfully" -Level "SUCCESS"
    }
    else {
        Write-Log "Failed to create VSCode settings backup" -Level "ERROR"
    }
}

# 1. УДАЛЕНИЕ УСТАНОВЛЕННЫХ ВЕРСИЙ PYTHON
Write-Host "[1/5] Searching for installed Python versions..." -ForegroundColor Yellow
$pythonInstallations = Get-ChildItem -Path @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
) | ForEach-Object { 
    Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
} | Where-Object { 
    $_.DisplayName -match "Python [0-9]+|Anaconda|Miniconda"
} | Select-Object DisplayName, UninstallString, PSPath

$uninstallCount = 0
if (-not $pythonInstallations) {
    Write-Host (Get-LocalizedString "NoPythonFound") -ForegroundColor Green
}
else {
    Write-Host (Get-LocalizedString "FoundVersions" -FormatArgs $pythonInstallations.Count) -ForegroundColor Cyan
    
    foreach ($install in $pythonInstallations) {
        if ($install.UninstallString) {
            try {
                # Подтверждение для важных удалений
                $confirm = $Force
                if (-not $Force) {
                    $title = Get-LocalizedString "RemovePython"
                    $question = Get-LocalizedString "RemoveVersion" -FormatArgs $install.DisplayName, $install.PSPath
                    $choices = @(
                        [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "Yes"), (Get-LocalizedString "RemoveThisVersion"))
                        [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "No"), (Get-LocalizedString "SkipThisVersion"))
                        [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "All"), (Get-LocalizedString "RemoveAllNoConfirm"))
                        [System.Management.Automation.Host.ChoiceDescription]::new((Get-LocalizedString "Cancel"), (Get-LocalizedString "AbortScript"))
                    )
                    
                    $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
                    
                    switch ($decision) {
                        0 { $confirm = $true }
                        1 { continue }
                        2 { $Force = $true; $confirm = $true }
                        3 { exit }
                    }
                }
                
                if ($confirm) {
                    # Форматирование строки удаления
                    $uninstallString = $install.UninstallString.Trim()
                    
                    if ($uninstallString -match "msiexec\.exe") {
                        # MSI установщик
                        $guidPattern = '\{([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\}'
                        if ($uninstallString -match $guidPattern) {
                            $msiGuid = $matches[0]
                            Write-Host (Get-LocalizedString "RemovingMSI" -FormatArgs $install.DisplayName, $msiGuid) -ForegroundColor Red
                            $process = Start-Process "msiexec.exe" -ArgumentList "/X $msiGuid /qn /norestart" -Wait -PassThru
                        }
                        else {
                            Write-Host "Failed to extract GUID for: $($install.DisplayName)" -ForegroundColor Red
                            continue
                        }
                    }
                    else {
                        # EXE установщик
                        Write-Host (Get-LocalizedString "RemovingEXE" -FormatArgs $install.DisplayName) -ForegroundColor Red
                        $process = Start-Process -FilePath $uninstallString -ArgumentList "/S" -Wait -PassThru
                    }
                    
                    if ($process.ExitCode -eq 0) {
                        $uninstallCount++
                        Write-Host (Get-LocalizedString "SuccessfullyRemoved" -FormatArgs $install.DisplayName) -ForegroundColor Green
                    }
                    else {
                        Write-Host (Get-LocalizedString "RemovalError" -FormatArgs $process.ExitCode, $install.DisplayName) -ForegroundColor Red
                    }
                }
            }
            catch {
                Write-Host (Get-LocalizedString "ErrorRemoving" -FormatArgs $install.DisplayName, $_.Exception.Message) -ForegroundColor Red
            }
        }
    }
}

# 2. УДАЛЕНИЕ ОСТАТОЧНЫХ ФАЙЛОВ PYTHON
Write-Host (Get-LocalizedString "RemovingResidual") -ForegroundColor Yellow
$pythonPaths = @(
    "${env:ProgramFiles}\Python*",
    "${env:LocalAppData}\Programs\Python*",
    "${env:AppData}\Python",
    "${env:UserProfile}\AppData\Local\Programs\Python",
    "${env:UserProfile}\AppData\Local\pip",
    "${env:UserProfile}\.python",
    "${env:UserProfile}\.conda",
    "${env:UserProfile}\.jupyter",
    "${env:UserProfile}\.ipython",
    "${env:ProgramData}\Anaconda*",
    "${env:ProgramData}\Miniconda*",
    "${env:ProgramFiles(x86)}\Python*",
    "${env:ProgramFiles(x86)}\Anaconda*",
    "${env:ProgramFiles(x86)}\Miniconda*"
)

$totalRemoved = 0
foreach ($path in $pythonPaths) {
    if (Remove-Safe -Path $path -Description (Get-LocalizedString "PythonFolder")) {
        $totalRemoved++
    }
}

# 3. ОЧИСТКА VSCODE
Write-Host (Get-LocalizedString "CleaningVSCode") -ForegroundColor Yellow
$vscodePaths = @(
    "${env:APPDATA}\Code\User\globalStorage\ms-python.python",
    "${env:APPDATA}\Code\Cache",
    "${env:APPDATA}\Code\CachedData",
    "${env:APPDATA}\Code\CachedExtensions",
    "${env:APPDATA}\Code\Local Storage",
    "${env:APPDATA}\Code\User\workspaceStorage",
    "${env:APPDATA}\Code\logs",
    "${env:APPDATA}\Code\Cache"
)

$vscodeCleaned = 0
foreach ($path in $vscodePaths) {
    if (Remove-Safe -Path $path -Description (Get-LocalizedString "VSCodeFolder")) {
        $vscodeCleaned++
    }
}

# Обработка settings.json
$settingsPath = "${env:APPDATA}\Code\User\settings.json"
if (Clean-VSCodeSettings -Path $settingsPath) {
    $vscodeCleaned++
}

# Удаление расширения Python
try {
    $codePath = Get-Command code -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    if ($codePath) {
        Write-Host (Get-LocalizedString "RemovingPythonExt") -ForegroundColor Blue
        & $codePath --uninstall-extension ms-python.python --force 2>$null
        Write-Host (Get-LocalizedString "PythonExtRemoved") -ForegroundColor Green
        $vscodeCleaned++
    }
    else {
        Write-Host (Get-LocalizedString "VSCodeNotFound") -ForegroundColor Yellow
    }
}
catch {
    Write-Host (Get-LocalizedString "ErrorRemovingExt" -FormatArgs $_.Exception.Message) -ForegroundColor Red
}

# 4. ОЧИСТКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
Write-Host (Get-LocalizedString "CleaningEnvVars") -ForegroundColor Yellow
$envVars = @(
    "PYTHONPATH",
    "PYTHONHOME",
    "ANACONDA_HOME",
    "VIRTUAL_ENV",
    "CONDA_PREFIX",
    "JUPYTER_CONFIG_DIR",
    "IPYTHONDIR",
    "PYTHONSTARTUP",
    "PYTHONDEBUG",
    "PYTHONUSERBASE"
)

$envVarsRemoved = 0
foreach ($var in $envVars) {
    try {
        $userValue = [Environment]::GetEnvironmentVariable($var, "User")
        $machineValue = [Environment]::GetEnvironmentVariable($var, "Machine")
        
        if ($userValue -or $machineValue) {
            [Environment]::SetEnvironmentVariable($var, $null, "User")
            [Environment]::SetEnvironmentVariable($var, $null, "Machine")
            Write-Host (Get-LocalizedString "RemovedVariable" -FormatArgs $var) -ForegroundColor DarkGray
            $envVarsRemoved++
        }
    }
    catch {
        Write-Log "Error removing variable ${var}: $($_.Exception.Message)" -Level "ERROR"
    }
}

# 5. УДАЛЕНИЕ ВИРТУАЛЬНЫХ ОКРУЖЕНИЙ
Write-Host (Get-LocalizedString "RemovingVenvs") -ForegroundColor Yellow
$venvPaths = @(
    "${env:UserProfile}\venv",
    "${env:UserProfile}\.virtualenvs",
    "${env:UserProfile}\.venv",
    "${env:UserProfile}\Envs",
    "${env:UserProfile}\.conda\envs",
    "${env:LocalAppData}\pypoetry\Cache",
    "${env:LocalAppData}\pip\Cache"
)

$venvRemoved = 0
foreach ($path in $venvPaths) {
    if (Remove-Safe -Path $path -Description (Get-LocalizedString "VirtualEnv")) {
        $venvRemoved++
    }
}

# Очистка PATH
Clear-PythonFromPath

# ИТОГОВОЕ СООБЩЕНИЕ
Write-Log (Get-LocalizedString "CleanupCompleted") -Level "INFO"
Write-Log (Get-LocalizedString "Results") -Level "INFO"
Write-Log (Get-LocalizedString "RemovedVersions" -FormatArgs $uninstallCount) -Level "INFO"
Write-Log (Get-LocalizedString "RemovedFolders" -FormatArgs $totalRemoved) -Level "INFO"
Write-Log (Get-LocalizedString "CleanedVSCode" -FormatArgs $vscodeCleaned) -Level "INFO"
Write-Log (Get-LocalizedString "RemovedEnvVars" -FormatArgs $envVarsRemoved) -Level "INFO"
Write-Log (Get-LocalizedString "RemovedVenvs" -FormatArgs $venvRemoved) -Level "INFO"

Write-Log (Get-LocalizedString "Recommendations") -Level "WARNING"
Write-Log (Get-LocalizedString "RestartPC") -Level "WARNING"
Write-Log (Get-LocalizedString "CheckPrograms") -Level "WARNING"
Write-Log (Get-LocalizedString "CheckEnvVars") -Level "WARNING"
Write-Log (Get-LocalizedString "ReinstallIfNeeded") -Level "WARNING"

# Запрос перед завершением
if (-not $Force) {
    Write-Log (Get-LocalizedString "PressAnyKey") -Level "INFO"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
