#!/bin/bash
# build.sh — build Range Box thành dist/RangeBox.dll (net10.0-windows, khớp Quantower 1.146.x).
# Gồm 3 file: RangeLogic.cs + RangeRenderer.cs + RangeBox.cs. qw-build.sh chỉ nhận 1 file nên tự tạo csproj tạm
# (EnableDefaultCompileItems=false để KHÔNG kéo tests/ vào). Chạy trong Git Bash; đường dẫn trong csproj là Windows (cygpath -w).
# Lỗi biên dịch HOẶC có cảnh báo CS => thoát mã 1.
#   Usage: bash quantower-range/build.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
LIBS="$HOME/quantower-libs"
for f in TradingPlatform.BusinessLayer.dll System.Drawing.Common.dll; do
  [ -f "$LIBS/$f" ] || { echo "build.sh: thiếu $LIBS/$f (xem quantower-orderflow-indicator/BUILD.md)" >&2; exit 1; }
done
TMP="$(mktemp -d)"
LIBS_W="$(cygpath -w "$LIBS")"; TMP_W="$(cygpath -w "$TMP")"
cat > "$TMP/RangeBox.csproj" <<EOF
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0-windows</TargetFramework>
    <EnableWindowsTargeting>true</EnableWindowsTargeting>
    <Nullable>disable</Nullable>
    <LangVersion>latest</LangVersion>
    <AssemblyName>RangeBox</AssemblyName>
    <RootNamespace>RangeBox</RootNamespace>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <AppendTargetFrameworkToOutputPath>false</AppendTargetFrameworkToOutputPath>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <NoWarn>CA1416;NU1701;MSB3277</NoWarn>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="TradingPlatform.BusinessLayer"><HintPath>$LIBS_W\TradingPlatform.BusinessLayer.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="System.Drawing.Common"><HintPath>$LIBS_W\System.Drawing.Common.dll</HintPath><Private>false</Private></Reference>
    <Compile Include="$(cygpath -w "$HERE/RangeLogic.cs")" />
    <Compile Include="$(cygpath -w "$HERE/RangeRenderer.cs")" />
    <Compile Include="$(cygpath -w "$HERE/RangeBox.cs")" />
  </ItemGroup>
</Project>
EOF
LOG="$TMP/build.log"
set +e
dotnet build "$TMP_W\\RangeBox.csproj" -c Release -o "$TMP_W\\out" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e
[ "$RC" -ne 0 ] && { echo "build.sh: CÓ LỖI BIÊN DỊCH" >&2; rm -rf "$TMP"; exit 1; }
if grep -E "warning CS" "$LOG" | grep -q .; then echo "build.sh: CÓ CẢNH BÁO — xem log trên" >&2; rm -rf "$TMP"; exit 1; fi
mkdir -p "$HERE/dist"
cp "$TMP/out/RangeBox.dll" "$HERE/dist/RangeBox.dll"
rm -rf "$TMP"
echo "==> $HERE/dist/RangeBox.dll"
