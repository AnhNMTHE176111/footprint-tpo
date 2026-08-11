# ============================================================================
#  deploy-windows.ps1 — cập nhật indicator vào Optimus Flow bằng 1 thao tác
# ============================================================================
#  Chạy trên máy Windows sau khi `git pull`: script tự copy các DLL trong repo
#  vào C:\OptimusFLOW\Settings\Scripts\Indicators đúng chỗ (folder con hoặc gốc
#  như đang bày sẵn trên máy), rồi in bảng kết quả.
#
#  Cách dùng: nháy đúp deploy-windows.bat (nó gọi file này), hoặc:
#     powershell -ExecutionPolicy Bypass -File deploy-windows.ps1
#     ... -NoPull            : không tự git pull, chỉ copy
#     ... -Dest "D:\..."     : đổi thư mục Indicators
#     ... -Only tpo          : chỉ đẩy nhóm khớp chữ này (tpo/entry/runner/...)
#
#  Optimus Flow ĐANG MỞ sẽ khoá file .dll → copy hỏng. Script phát hiện và báo
#  rõ file nào bị khoá; đóng Optimus Flow rồi chạy lại là xong.
# ============================================================================
param(
    [string]$Dest = "C:\OptimusFLOW\Settings\Scripts\Indicators",
    [switch]$NoPull,
    [string]$Only = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path

# Bản đồ: DLL trong repo  →  thư mục con dưới Indicators ("" = đặt ngay gốc).
# Giữ ĐÚNG cách bày hiện tại trên máy Windows (ảnh chụp 2026-08-11).
$map = @(
    @{ src = "quantower-tpo-suite\dist\DailyTpoBias.dll";        dir = "TPO Suite" }
    @{ src = "quantower-tpo-suite\dist\SessionZones.dll";        dir = "TPO Suite" }
    @{ src = "quantower-entry-signal\dist\EntrySignal.dll";      dir = "EntrySignal" }
    @{ src = "quantower-entry-signal\dist\RunnerSignal.dll";     dir = "" }
    @{ src = "quantower-entry-signal\dist\WyckoffRunner.dll";    dir = "" }
    @{ src = "quantower-footprint-export\dist\FootprintExport.dll"; dir = "" }
    @{ src = "quantower-askbid-delta\dist\AskBidDeltaBars.dll";  dir = "AskBidDeltaBars" }
    @{ src = "quantower-dma\dist\DeltaMovingAverage.dll";        dir = "DeltaMovingAverage" }
    @{ src = "quantower-orderflow-indicator\dist\OrderFlowBubbles.dll"; dir = "OrderFlowBubbles" }
    @{ src = "quantower-vsa-volume\dist\VsaVolume.dll";          dir = "VsaVolume" }
)

Write-Host ""
Write-Host "=== Cap nhat indicator vao Optimus Flow ===" -ForegroundColor Cyan
Write-Host "Repo : $repo"
Write-Host "Dich : $Dest"
Write-Host ""

# ---- 1. Kéo code mới ----
if (-not $NoPull) {
    Write-Host "[1/3] git pull ..." -ForegroundColor Yellow
    Push-Location $repo
    try {
        git pull --ff-only
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  git pull LOI (co thay doi chua commit?) — van tiep tuc copy ban dang co." -ForegroundColor Red
        }
    } catch {
        Write-Host "  Khong chay duoc git: $($_.Exception.Message)" -ForegroundColor Red
    } finally { Pop-Location }
} else {
    Write-Host "[1/3] Bo qua git pull (-NoPull)" -ForegroundColor DarkGray
}

if (-not (Test-Path $Dest)) {
    Write-Host "KHONG thay thu muc dich: $Dest" -ForegroundColor Red
    Write-Host "Chay lai voi: -Dest ""duong\dan\Indicators""" -ForegroundColor Red
    exit 1
}

# ---- 2. Optimus Flow con dang mo? ----
Write-Host "[2/3] Kiem tra Optimus Flow ..." -ForegroundColor Yellow
$proc = Get-Process -Name "OptimusFlow", "Quantower", "Starter" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "  Optimus Flow/Quantower DANG CHAY — file .dll co the bi khoa." -ForegroundColor Red
    Write-Host "  Nen dong han phan mem roi chay lai script nay." -ForegroundColor Red
    $ans = Read-Host "  Van thu copy? (y/N)"
    if ($ans -ne "y") { exit 1 }
} else {
    Write-Host "  OK, khong thay tien trinh nao dang mo." -ForegroundColor Green
}

# ---- 3. Copy ----
Write-Host "[3/3] Copy DLL ..." -ForegroundColor Yellow
$okCount = 0; $skipCount = 0; $failCount = 0
foreach ($m in $map) {
    $srcPath = Join-Path $repo $m.src
    $name = Split-Path $m.src -Leaf
    if ($Only -and ($m.src -notmatch [regex]::Escape($Only)) -and ($name -notmatch [regex]::Escape($Only))) { continue }

    if (-not (Test-Path $srcPath)) {
        Write-Host ("  - {0,-22} khong co trong repo (chua build)" -f $name) -ForegroundColor DarkGray
        $skipCount++
        continue
    }
    $dstDir = if ($m.dir) { Join-Path $Dest $m.dir } else { $Dest }
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
    $dstPath = Join-Path $dstDir $name

    # Bo qua neu file dich da y het (cung kich thuoc + cung thoi gian sua)
    if (Test-Path $dstPath) {
        $s = Get-Item $srcPath; $d = Get-Item $dstPath
        if ($s.Length -eq $d.Length -and $s.LastWriteTimeUtc -le $d.LastWriteTimeUtc) {
            Write-Host ("  = {0,-22} da moi nhat" -f $name) -ForegroundColor DarkGray
            $skipCount++
            continue
        }
    }
    try {
        Copy-Item $srcPath $dstPath -Force
        $where = if ($m.dir) { "$($m.dir)\" } else { "(goc)" }
        Write-Host ("  + {0,-22} -> {1}" -f $name, $where) -ForegroundColor Green
        $okCount++
    } catch {
        Write-Host ("  ! {0,-22} LOI: {1}" -f $name, $_.Exception.Message) -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "Xong: $okCount cap nhat, $skipCount bo qua, $failCount loi." -ForegroundColor Cyan
if ($failCount -gt 0) {
    Write-Host "File loi thuong do Optimus Flow dang mo giu file — dong phan mem roi chay lai." -ForegroundColor Red
}
Write-Host "Mo lai Optimus Flow, indicator se dung ban moi (Quantower doc DLL luc khoi dong)."
Write-Host ""
if ($Host.Name -eq "ConsoleHost" -and -not $env:CI) { Read-Host "Enter de dong" | Out-Null }
