<#
  ============================================================================
  push-atas-dlls.ps1
  ----------------------------------------------------------------------------
  Gom cac file DLL cua ATAS (nguyen lieu de build) tu may Windows nay
  va DAY LEN GitHub, de Claude keo ve compile ho ra OrderFlowBubbles.dll.

  Chi can chay 1 LAN. Yeu cau: da cai Git (neu chua, script se bao cach cai).
  Lan push dau tien se hien cua so dang nhap GitHub -> dang nhap tai khoan cua ban.
  ============================================================================
#>
$ErrorActionPreference = "Stop"

# === Chinh o day neu ATAS cai cho khac ===
$AtasDir = "C:\Program Files (x86)\ATAS Platform"
$RepoUrl = "https://github.com/AnhNMTHE176111/footprint-tpo.git"
$Work    = Join-Path $env:USERPROFILE "footprint-tpo-build"
$LibsRel = "atas-orderflow-indicator\libs"

Write-Host "=== 1/5 Kiem tra Git ===" -ForegroundColor Cyan
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "CHUA CO GIT." -ForegroundColor Red
    Write-Host "Cai bang lenh:   winget install Git.Git" -ForegroundColor Yellow
    Write-Host "Roi MO POWERSHELL MOI va chay lai script nay." -ForegroundColor Yellow
    Write-Host "(Neu winget khong chay: tai Git tai https://git-scm.com/download/win )" -ForegroundColor Yellow
    return
}

Write-Host "=== 2/5 Kiem tra thu muc ATAS ===" -ForegroundColor Cyan
if (-not (Test-Path $AtasDir)) {
    Write-Host "Khong thay thu muc ATAS: $AtasDir" -ForegroundColor Red
    Write-Host "Sua bien \$AtasDir o dau script cho dung duong dan cai ATAS cua ban." -ForegroundColor Yellow
    return
}

Write-Host "=== 3/5 Clone / cap nhat repo ===" -ForegroundColor Cyan
if (Test-Path (Join-Path $Work ".git")) {
    git -C $Work checkout main | Out-Null
    git -C $Work pull --no-edit
} else {
    git clone $RepoUrl $Work
}

Write-Host "=== 4/5 Copy DLL (ATAS.* / OFT.* / Utils.*) vao libs\ ===" -ForegroundColor Cyan
$Dst = Join-Path $Work $LibsRel
New-Item -ItemType Directory -Force -Path $Dst | Out-Null
$dlls = Get-ChildItem "$AtasDir\*.dll" | Where-Object {
    $_.Name -match '^(ATAS|OFT|Utils)\.' -and $_.Name -notmatch 'DevExpress'
}
if ($dlls.Count -eq 0) {
    Write-Host "Khong tim thay DLL ATAS/OFT/Utils trong $AtasDir" -ForegroundColor Red
    return
}
$dlls | Copy-Item -Destination $Dst -Force
Write-Host ("Da copy {0} file DLL." -f $dlls.Count) -ForegroundColor Green
$dlls | ForEach-Object { Write-Host ("   - " + $_.Name) }

Write-Host "=== 5/5 Commit + push len GitHub ===" -ForegroundColor Cyan
git -C $Work add -f "$LibsRel\*.dll"
$pending = git -C $Work status --porcelain
if ([string]::IsNullOrWhiteSpace($pending)) {
    Write-Host "Khong co thay doi moi (co le DLL da day truoc do). Van OK." -ForegroundColor Yellow
} else {
    git -C $Work commit -m "Them DLL ATAS de build OrderFlowBubbles (tam thoi, Claude se xoa sau)"
    Write-Host "Dang push... (lan dau hien cua so dang nhap GitHub -> dang nhap la xong)" -ForegroundColor Yellow
    git -C $Work push origin main
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " XONG! Da day DLL len GitHub." -ForegroundColor Green
Write-Host " Quay lai chat va bao Claude: 'day DLL xong roi'." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
