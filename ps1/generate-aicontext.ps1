# powershell -ExecutionPolicy Bypass -File E:\git\igaponr\training\ps1\generate-aicontext.ps1
# 1. スクリプトがあるフォルダのパスを取得
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
}

# 2. パスの設定
$configFile = Join-Path $ScriptRoot "..\config\config.json"
$outputFile = Join-Path $ScriptRoot "ai_context.md"

# 設定ファイルの存在確認
if (-not (Test-Path $configFile)) {
    Write-Error "Error: Configuration file not found at: $configFile"
    exit
}

# JSONの読み込み
try {
    $jsonRaw = Get-Content $configFile -Raw -Encoding utf8 -ErrorAction Stop
    $config = $jsonRaw | ConvertFrom-Json
} catch {
    Write-Error "Error: Failed to parse JSON. Path: $configFile"
    exit
}

# 出力ファイルを初期化
"" | Out-File -FilePath $outputFile -Encoding utf8 -Force

Write-Host "--- Process Started ---" -ForegroundColor Cyan
Write-Host "Script Directory: $ScriptRoot"
Write-Host "Config File: $configFile"
Write-Host "Output File: $outputFile"
Write-Host "-----------------------"

foreach ($folderPath in $config.folders) {
    # フォルダパスが相対パスの場合は、スクリプト基準で絶対パスに変換
    $absoluteFolder = $folderPath
    if (-not [System.IO.Path]::IsPathRooted($folderPath)) {
        $absoluteFolder = [System.IO.Path]::GetFullPath((Join-Path $ScriptRoot $folderPath))
    }

    if (-not (Test-Path $absoluteFolder)) {
        Write-Warning "Folder not found: $absoluteFolder"
        continue
    }

    Write-Host "Scanning: $absoluteFolder" -ForegroundColor Yellow

    foreach ($ext in $config.extensions) {
        $files = Get-ChildItem -Path $absoluteFolder -Filter "*$ext" -File -Recurse -ErrorAction SilentlyContinue

        foreach ($file in $files) {
            Write-Host "  Adding: $($file.Name)"

            $fullPath = $file.FullName
            $content = Get-Content $fullPath -Raw -ErrorAction SilentlyContinue

            if ($null -eq $content) { continue }

            $lang = $ext.Replace(".", "")
            $mdHeader = "`n---`n### File: $($fullPath)`n" + "``````$lang`n"
            $mdFooter = "`n``````"

            $mdHeader | Out-File -FilePath $outputFile -Append -Encoding utf8
            $content  | Out-File -FilePath $outputFile -Append -Encoding utf8
            $mdFooter  | Out-File -FilePath $outputFile -Append -Encoding utf8
        }
    }
}

Write-Host "`nSuccessfully completed!" -ForegroundColor Green
Write-Host "Check output: $outputFile"
