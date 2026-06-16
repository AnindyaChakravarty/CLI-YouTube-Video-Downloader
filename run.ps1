$ErrorActionPreference = "Stop"

try {

    # ------------------------------------------------------------
    # Project root
    # ------------------------------------------------------------

    $ProjectRoot = $PSScriptRoot
    Set-Location $ProjectRoot

    # ------------------------------------------------------------
    # Utility functions
    # ------------------------------------------------------------

    function Stop-WithError {
        param (
            [string]$Message,
            [int]$Code = 1
        )

        Write-Host ""
        Write-Host "ERROR: $Message" -ForegroundColor Red
        Write-Host ""
        exit $Code
    }

    function Write-Ok {
        param ([string]$Message)
        Write-Host "[OK] $Message" -ForegroundColor Green
    }

    function Write-Info {
        param ([string]$Message)
        Write-Host "[..] $Message"
    }

    function Invoke-QuietCommand {
        param (
            [scriptblock]$Command,
            [string]$ErrorMessage
        )

        try {
            $Output = & $Command 2>&1
            $Code = $LASTEXITCODE

            if ($null -eq $Code) {
                $Code = 0
            }

            if ($Code -ne 0) {
                Write-Host ""
                Write-Host "Command output:" -ForegroundColor Yellow
                $Output | ForEach-Object { Write-Host $_ }
                Stop-WithError $ErrorMessage $Code
            }
        }
        catch {
            Write-Host ""
            Write-Host "Command output:" -ForegroundColor Yellow
            Write-Host $_.Exception.Message
            Stop-WithError $ErrorMessage 1
        }
    }

    function Invoke-VisibleCommand {
        param (
            [scriptblock]$Command,
            [string]$ErrorMessage
        )

        try {
            & $Command

            $Code = $LASTEXITCODE

            if ($null -eq $Code) {
                $Code = 0
            }

            if ($Code -ne 0) {
                Stop-WithError $ErrorMessage $Code
            }
        }
        catch {
            Write-Host ""
            Write-Host "Command output:" -ForegroundColor Yellow
            Write-Host $_.Exception.Message
            Stop-WithError $ErrorMessage 1
        }
    }

    function Update-SessionPath {
        $MachinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")

        if ($MachinePath -and $UserPath) {
            $env:Path = "$MachinePath;$UserPath"
        }
        elseif ($MachinePath) {
            $env:Path = $MachinePath
        }
        elseif ($UserPath) {
            $env:Path = $UserPath
        }
    }

    function Add-DirectoryToSessionPath {
        param ([string]$DirectoryPath)

        if (-not $DirectoryPath) {
            return
        }

        if (-not (Test-Path $DirectoryPath)) {
            return
        }

        $CurrentParts = $env:Path -split ";" | Where-Object { $_ -ne "" }

        foreach ($Part in $CurrentParts) {
            if ($Part.TrimEnd("\") -ieq $DirectoryPath.TrimEnd("\")) {
                return
            }
        }

        $env:Path = "$DirectoryPath;$env:Path"
    }

    function Add-DirectoryToUserPath {
        param ([string]$DirectoryPath)

        if (-not $DirectoryPath) {
            return
        }

        if (-not (Test-Path $DirectoryPath)) {
            return
        }

        $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")

        if (-not $UserPath) {
            [Environment]::SetEnvironmentVariable("Path", $DirectoryPath, "User")
            return
        }

        $ExistingParts = $UserPath -split ";" | Where-Object { $_ -ne "" }

        foreach ($Part in $ExistingParts) {
            if ($Part.TrimEnd("\") -ieq $DirectoryPath.TrimEnd("\")) {
                return
            }
        }

        $NewUserPath = "$UserPath;$DirectoryPath"
        [Environment]::SetEnvironmentVariable("Path", $NewUserPath, "User")
    }

    # ------------------------------------------------------------
    # Python detection
    # ------------------------------------------------------------

    $PythonExe = $null
    $PythonArgs = @()

    function Set-PythonCommand {
        param (
            [string]$Exe,
            [string[]]$PythonCommandArgs = @()
        )

        $script:PythonExe = $Exe
        $script:PythonArgs = $PythonCommandArgs
    }

    function Test-WindowsPythonAlias {
        param ([string]$Path)

        if (-not $Path) {
            return $false
        }

        return (
            $Path -like "*\AppData\Local\Microsoft\WindowsApps\python.exe" -or
            $Path -like "*\AppData\Local\Microsoft\WindowsApps\python3.exe"
        )
    }

    function Test-PythonCommand {
        param (
            [string]$Exe,
            [string[]]$PythonCommandArgs = @()
        )

        $PreviousErrorActionPreference = $ErrorActionPreference

        try {
            $ErrorActionPreference = "SilentlyContinue"

            & $Exe @PythonCommandArgs -c "import sys; exit(0 if sys.version_info.major == 3 else 1)" 1>$null 2>$null

            $Code = $LASTEXITCODE

            return ($Code -eq 0)
        }
        catch {
            return $false
        }
        finally {
            $ErrorActionPreference = $PreviousErrorActionPreference
        }
    }

    function Find-Python {
        $script:PythonExe = $null
        $script:PythonArgs = @()

        # 1. Preferred Windows Python launcher
        $PyCommand = Get-Command py -ErrorAction SilentlyContinue

        if ($PyCommand) {
            if (Test-PythonCommand "py" @("-3")) {
                Set-PythonCommand "py" @("-3")
                return $true
            }
        }

        # 2. python from PATH, but ignore Microsoft Store alias
        $PythonCommand = Get-Command python -ErrorAction SilentlyContinue

        if ($PythonCommand) {
            $PythonPath = $PythonCommand.Source

            if (-not (Test-WindowsPythonAlias $PythonPath)) {
                if (Test-PythonCommand "python") {
                    Set-PythonCommand "python"
                    return $true
                }
            }
        }

        # 3. python3 from PATH, but ignore Microsoft Store alias
        $Python3Command = Get-Command python3 -ErrorAction SilentlyContinue

        if ($Python3Command) {
            $Python3Path = $Python3Command.Source

            if (-not (Test-WindowsPythonAlias $Python3Path)) {
                if (Test-PythonCommand "python3") {
                    Set-PythonCommand "python3"
                    return $true
                }
            }
        }

        # 4. Common real Python installation folders
        $PossiblePythonFiles = @()

        $SearchRoots = @(
            "$env:LOCALAPPDATA\Programs\Python",
            "C:\Program Files",
            "C:\Program Files (x86)"
        )

        foreach ($Root in $SearchRoots) {
            if (Test-Path $Root) {
                $PossiblePythonFiles += Get-ChildItem `
                    -Path $Root `
                    -Recurse `
                    -Filter "python.exe" `
                    -ErrorAction SilentlyContinue
            }
        }

        foreach ($Candidate in $PossiblePythonFiles) {
            if (-not (Test-WindowsPythonAlias $Candidate.FullName)) {
                if (Test-PythonCommand $Candidate.FullName) {
                    Set-PythonCommand $Candidate.FullName
                    return $true
                }
            }
        }

        return $false
    }

    function Invoke-Python {
        param ([string[]]$PythonScriptArgs)

        & $script:PythonExe @script:PythonArgs @PythonScriptArgs
    }

    # ------------------------------------------------------------
    # FFmpeg detection
    # ------------------------------------------------------------

    $FfmpegExe = $null
    $FfmpegBinDir = $null

    function Set-FFmpegCommand {
        param ([string]$Exe)

        $script:FfmpegExe = $Exe
        $script:FfmpegBinDir = Split-Path -Parent $Exe
    }

    function Test-FFmpegCommand {
        param ([string]$Exe)

        try {
            & $Exe -version 1>$null 2>$null
            return ($LASTEXITCODE -eq 0)
        }
        catch {
            return $false
        }
    }

    function Find-FFmpeg {
        $script:FfmpegExe = $null
        $script:FfmpegBinDir = $null

        # 1. ffmpeg from PATH
        $FFmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue

        if ($FFmpegCommand) {
            if (Test-FFmpegCommand $FFmpegCommand.Source) {
                Set-FFmpegCommand $FFmpegCommand.Source
                return $true
            }
        }

        # 2. Common FFmpeg and package-manager locations
        $PossibleFFmpegFiles = @()

        $SearchRoots = @(
            "$env:LOCALAPPDATA\Microsoft\WinGet\Links",
            "$env:LOCALAPPDATA\Microsoft\WinGet\Packages",
            "$env:ProgramFiles\WinGet\Links",
            "$env:ProgramFiles\WinGet\Packages",
            "${env:ProgramFiles(x86)}\WinGet\Links",
            "${env:ProgramFiles(x86)}\WinGet\Packages",
            "$env:ProgramData\chocolatey\bin",
            "$env:USERPROFILE\scoop\shims",
            "$env:LOCALAPPDATA\Programs\ffmpeg",
            "C:\ffmpeg",
            "C:\Program Files\ffmpeg",
            "C:\Program Files (x86)\ffmpeg"
        )

        foreach ($Root in $SearchRoots) {
            if ($Root -and (Test-Path $Root)) {
                $PossibleFFmpegFiles += Get-ChildItem `
                    -Path $Root `
                    -Recurse `
                    -Filter "ffmpeg.exe" `
                    -ErrorAction SilentlyContinue
            }
        }

        foreach ($Candidate in $PossibleFFmpegFiles) {
            if (Test-FFmpegCommand $Candidate.FullName) {
                Set-FFmpegCommand $Candidate.FullName
                return $true
            }
        }

        return $false
    }

    function Install-FFmpeg {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Stop-WithError "FFmpeg is not installed and winget is not available. Install App Installer/winget or install FFmpeg manually."
        }

        Invoke-VisibleCommand {
            winget install `
                --id Gyan.FFmpeg `
                -e `
                --source winget `
                --accept-package-agreements `
                --accept-source-agreements
        } "Failed to install FFmpeg."

        Update-SessionPath

        # WinGet portable command aliases commonly live here.
        $UserWinGetLinks = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links"
        $MachineWinGetLinks = Join-Path $env:ProgramFiles "WinGet\Links"

        Add-DirectoryToSessionPath $UserWinGetLinks
        Add-DirectoryToSessionPath $MachineWinGetLinks
        Add-DirectoryToUserPath $UserWinGetLinks
    }

    # ------------------------------------------------------------
    # Deno detection
    # ------------------------------------------------------------

    $DenoExe = $null
    $DenoBinDir = $null

    function Set-DenoCommand {
        param ([string]$Exe)

        $script:DenoExe = $Exe
        $script:DenoBinDir = Split-Path -Parent $Exe
    }

    function Test-DenoCommand {
        param ([string]$Exe)

        try {
            & $Exe --version 1>$null 2>$null
            return ($LASTEXITCODE -eq 0)
        }
        catch {
            return $false
        }
    }

    function Find-Deno {
        $script:DenoExe = $null
        $script:DenoBinDir = $null

        # 1. deno from PATH
        $DenoCommand = Get-Command deno -ErrorAction SilentlyContinue

        if ($DenoCommand) {
            if (Test-DenoCommand $DenoCommand.Source) {
                Set-DenoCommand $DenoCommand.Source
                return $true
            }
        }

        # 2. Common Deno locations
        $PossibleDenoFiles = @()

        $SearchRoots = @(
            "$env:DENO_INSTALL\bin",
            "$env:USERPROFILE\.deno\bin",
            "$env:LOCALAPPDATA\Microsoft\WinGet\Links",
            "$env:LOCALAPPDATA\Microsoft\WinGet\Packages",
            "$env:ProgramFiles\WinGet\Links",
            "$env:ProgramFiles\WinGet\Packages",
            "${env:ProgramFiles(x86)}\WinGet\Links",
            "${env:ProgramFiles(x86)}\WinGet\Packages",
            "$env:ProgramData\chocolatey\bin",
            "$env:USERPROFILE\scoop\shims",
            "$env:LOCALAPPDATA\Programs\deno",
            "C:\Program Files\deno",
            "C:\Program Files (x86)\deno"
        )

        foreach ($Root in $SearchRoots) {
            if ($Root -and (Test-Path $Root)) {
                $PossibleDenoFiles += Get-ChildItem `
                    -Path $Root `
                    -Recurse `
                    -Filter "deno.exe" `
                    -ErrorAction SilentlyContinue
            }
        }

        foreach ($Candidate in $PossibleDenoFiles) {
            if (Test-DenoCommand $Candidate.FullName) {
                Set-DenoCommand $Candidate.FullName
                return $true
            }
        }

        return $false
    }

    function Install-Deno {
    $DefaultDenoInstall = Join-Path $env:USERPROFILE ".deno"
    $DefaultDenoBin = Join-Path $DefaultDenoInstall "bin"

    # Keep the install target predictable for this script session.
    $env:DENO_INSTALL = $DefaultDenoInstall

    # Also persist DENO_INSTALL for future sessions.
    [Environment]::SetEnvironmentVariable("DENO_INSTALL", $DefaultDenoInstall, "User")

    Invoke-VisibleCommand {
        Invoke-RestMethod https://deno.land/install.ps1 | Invoke-Expression
    } "Failed to install Deno."

    # Make deno available in the current launcher session.
    Add-DirectoryToSessionPath $DefaultDenoBin

    # Make deno available in future terminals.
    Add-DirectoryToUserPath $DefaultDenoBin

    # Reload PATH from Machine/User environment, then ensure Deno is still present.
    Update-SessionPath
    Add-DirectoryToSessionPath $DefaultDenoBin
    }

    # ------------------------------------------------------------
    # Start
    # ------------------------------------------------------------

    Write-Host ""
    Write-Host "Starting project..." -ForegroundColor Cyan
    Write-Host ""

    # ------------------------------------------------------------
    # Check/install Python
    # ------------------------------------------------------------

    Write-Info "Checking Python"

    Update-SessionPath

    if (-not (Find-Python)) {
        Write-Info "Python not found. Attempting installation"

        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Stop-WithError "Python is not installed and winget is not available. Install Python manually from python.org, then run this launcher again."
        }

        Invoke-VisibleCommand {
            winget install `
                --id Python.Python.3.12 `
                -e `
                --source winget `
                --accept-package-agreements `
                --accept-source-agreements
        } "Failed to install Python."

        Update-SessionPath

        if (-not (Find-Python)) {
            Stop-WithError "Python was installed, but this terminal cannot find it yet. Close this window and double-click start.bat again."
        }
    }

    Write-Ok "Python available"

    # ------------------------------------------------------------
    # Check/install FFmpeg
    # ------------------------------------------------------------

    Write-Info "Checking FFmpeg"

    Update-SessionPath

    if (-not (Find-FFmpeg)) {
        Write-Info "FFmpeg not found. Attempting installation"

        Install-FFmpeg

        if (-not (Find-FFmpeg)) {
            Stop-WithError "FFmpeg was installed, but this terminal cannot find it yet. Close this window and double-click start.bat again."
        }
    }

    if ($FfmpegBinDir) {
        Add-DirectoryToSessionPath $FfmpegBinDir
        Add-DirectoryToUserPath $FfmpegBinDir
    }

    Write-Ok "FFmpeg available"

    # ------------------------------------------------------------
    # Check/install Deno
    # ------------------------------------------------------------

    Write-Info "Checking Deno"

    Update-SessionPath

    if (-not (Find-Deno)) {
        Write-Info "Deno not found. Attempting installation"

        Install-Deno

        if (-not (Find-Deno)) {
            Stop-WithError "Deno was installed, but this terminal cannot find it yet. Close this window and double-click start.bat again."
        }
    }

    if ($DenoBinDir) {
        Add-DirectoryToSessionPath $DenoBinDir
        Add-DirectoryToUserPath $DenoBinDir
    }

    Write-Ok "Deno available"

    # ------------------------------------------------------------
    # Create/check virtual environment
    # ------------------------------------------------------------

    $VenvDir = Join-Path $ProjectRoot ".venv"

    if (-not (Test-Path $VenvDir)) {
        Write-Info "Creating virtual environment"

        Invoke-QuietCommand {
            Invoke-Python @("-m", "venv", $VenvDir)
        } "Failed to create virtual environment."
    }

    Write-Ok "Virtual environment ready"

    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    $VenvScripts = Join-Path $VenvDir "Scripts"

    if (-not (Test-Path $VenvPython)) {
        Stop-WithError "Virtual environment is broken. Missing .venv\Scripts\python.exe. Delete .venv and run this launcher again."
    }

    # Activate venv for this script session without relying on Activate.ps1
    $env:VIRTUAL_ENV = $VenvDir
    $env:Path = "$VenvScripts;$env:Path"

    Write-Ok "Virtual environment activated"

    # ------------------------------------------------------------
    # Check requirements file
    # ------------------------------------------------------------

    $RequirementsTxt = Join-Path $ProjectRoot "requirements.txt"
    $RequirementsText = Join-Path $ProjectRoot "requirements.text"

    if (Test-Path $RequirementsTxt) {
        $RequirementsFile = $RequirementsTxt
    }
    elseif (Test-Path $RequirementsText) {
        $RequirementsFile = $RequirementsText
    }
    else {
        Stop-WithError "Missing requirements.txt."
    }

    # ------------------------------------------------------------
    # Install/check dependencies
    # ------------------------------------------------------------

    Write-Info "Checking dependencies"

    Invoke-VisibleCommand {
        & $VenvPython -m pip install `
            --disable-pip-version-check `
            --upgrade pip
    } "Failed to upgrade pip."

    Invoke-VisibleCommand {
        & $VenvPython -m pip install `
            --disable-pip-version-check `
            -r $RequirementsFile
    } "Failed to install dependencies from requirements file."

    Write-Ok "Dependencies ready"

    # ------------------------------------------------------------
    # Check project files
    # ------------------------------------------------------------

    $RequiredPythonFiles = @(
        "main.py",
        "downloader.py",
        "logger.py",
        "playlist.py"
    )

    $MissingFiles = @()

    foreach ($File in $RequiredPythonFiles) {
        $FullPath = Join-Path $ProjectRoot $File

        if (-not (Test-Path $FullPath -PathType Leaf)) {
            $MissingFiles += $File
        }
    }

    if ($MissingFiles.Count -gt 0) {
        Stop-WithError "Missing required file(s): $($MissingFiles -join ', ')"
    }

    Write-Ok "Project files found"

    # ------------------------------------------------------------
    # Run main.py
    # ------------------------------------------------------------

    Clear-Host

    & $VenvPython (Join-Path $ProjectRoot "main.py")

    $ExitCode = $LASTEXITCODE

    if ($ExitCode -ne 0) {
        Stop-WithError "main.py exited with error code $ExitCode." $ExitCode
    }

    exit 0

}
catch {
    Write-Host ""
    Write-Host "UNHANDLED ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    if ($_.ScriptStackTrace) {
        Write-Host ""
        Write-Host "Stack trace:" -ForegroundColor Yellow
        Write-Host $_.ScriptStackTrace
    }

    Write-Host ""
    exit 1
}