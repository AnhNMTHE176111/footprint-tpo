#!/bin/bash
# Build FootprintExport.dll cho Quantower TREN LINUX (Quantower la app Windows,
# nhung DLL indicator van build cross-platform duoc: net10.0-windows + EnableWindowsTargeting).
#   Usage: ./build.sh
# Ra: dist/FootprintExport.dll  -> copy sang may Windows:
#   <Quantower>\Settings\Scripts\Indicators\FootprintExport\FootprintExport.dll
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
LIBS="$HOME/quantower-libs"
ASM="FootprintExport"
export PATH="$HOME/.dotnet:$PATH" DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1

[ -f "$LIBS/TradingPlatform.BusinessLayer.dll" ] || {
  echo "Khong thay $LIBS/TradingPlatform.BusinessLayer.dll — xem BUILD.md cua quantower-orderflow-indicator"; exit 1; }

B="$(mktemp -d)"
cp "$HERE/FootprintCore.cs" "$HERE/FootprintExport.cs" "$B/"
cat > "$B/build.csproj" <<CSPROJ
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0-windows</TargetFramework>
    <EnableWindowsTargeting>true</EnableWindowsTargeting>
    <Nullable>disable</Nullable>
    <LangVersion>latest</LangVersion>
    <AssemblyName>$ASM</AssemblyName>
    <RootNamespace>$ASM</RootNamespace>
    <AppendTargetFrameworkToOutputPath>false</AppendTargetFrameworkToOutputPath>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <NoWarn>CA1416</NoWarn>
    <TreatWarningsAsErrors>false</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="TradingPlatform.BusinessLayer"><HintPath>$LIBS/TradingPlatform.BusinessLayer.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="System.Drawing.Common"><HintPath>$LIBS/System.Drawing.Common.dll</HintPath><Private>false</Private></Reference>
  </ItemGroup>
</Project>
CSPROJ
dotnet build "$B/build.csproj" -c Release 2>&1 | tail -20
mkdir -p "$HERE/dist"
cp "$B/bin/Release/$ASM.dll" "$HERE/dist/$ASM.dll"
echo "==> Da build: $HERE/dist/$ASM.dll"
rm -rf "$B"
