param(
    [int]$Port = 8002
)

$ErrorActionPreference = "Stop"

$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $BackendDir ".venv312"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

function Find-Python312 {
    $candidates = @(
        @("py", "-3.12"),
        @("uv", "python", "find", "3.12"),
        @("python", "")
    )

    foreach ($candidate in $candidates) {
        $command = $candidate[0]
        $args = @()
        if ($candidate.Length -gt 1) {
            $args = $candidate[1..($candidate.Length - 1)] | Where-Object { $_ }
        }

        try {
            if ($command -eq "uv") {
                $path = & $command @args 2>$null
                if ($LASTEXITCODE -eq 0 -and $path) {
                    $version = & $path --version 2>$null
                    if ($version -match "Python 3\.12\.") {
                        return @($path)
                    }
                }
            } else {
                $version = & $command @args --version 2>$null
                if ($LASTEXITCODE -eq 0 -and $version -match "Python 3\.12\.") {
                    return @($command) + $args
                }
            }
        } catch {
            continue
        }
    }

    throw "Python 3.12 was not found. Install Python 3.12, then rerun this script."
}

Set-Location $BackendDir

if (-not (Test-Path $PythonExe)) {
    Write-Host "Creating backend virtual environment with Python 3.12..."
    $pythonCmd = Find-Python312
    $pythonArgs = @()
    if ($pythonCmd.Length -gt 1) {
        $pythonArgs = $pythonCmd[1..($pythonCmd.Length - 1)] | Where-Object { $_ }
    }
    & $pythonCmd[0] @pythonArgs -m venv $VenvDir
}

Write-Host "Using $(& $PythonExe --version) at $PythonExe"
& $PythonExe -m pip install -r requirements.txt

Write-Host "Starting AnomlyX backend on http://127.0.0.1:$Port"
& $PythonExe -m uvicorn app.main:app --host 127.0.0.1 --port $Port
