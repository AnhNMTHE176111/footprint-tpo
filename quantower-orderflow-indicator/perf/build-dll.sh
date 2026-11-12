#!/bin/bash
# Build dist/OrderFlowBubbles.dll tu 7 file nguon (xem BUILD.md). Chay tren Git Bash (Windows).
#   ./perf/build-dll.sh            -> build ra dist/OrderFlowBubbles.dll
# Can: .NET SDK (dotnet) + $HOME/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common}.dll
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"          # thu muc quantower-orderflow-indicator
LIBS="$HOME/quantower-libs"
B="$(mktemp -d)"
HERE_W="$(cygpath -w "$HERE")"; LIBS_W="$(cygpath -w "$LIBS")"; B_W="$(cygpath -w "$B")"
EXTRA=""
[ -f "$LIBS/System.Private.Windows.Core.dll" ] && EXTRA="<Reference Include=\"System.Private.Windows.Core\"><HintPath>$LIBS_W\System.Private.Windows.Core.dll</HintPath><Private>false</Private></Reference>"
cat > "$B/proj.csproj" <<XML
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0-windows</TargetFramework>
    <EnableWindowsTargeting>true</EnableWindowsTargeting>
    <Nullable>disable</Nullable>
    <LangVersion>latest</LangVersion>
    <AssemblyName>OrderFlowBubbles</AssemblyName>
    <RootNamespace>OrderFlowBubbles</RootNamespace>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <AppendTargetFrameworkToOutputPath>false</AppendTargetFrameworkToOutputPath>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <NoWarn>CA1416;NU1701;MSB3277;CS0649</NoWarn>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="TradingPlatform.BusinessLayer"><HintPath>$LIBS_W\TradingPlatform.BusinessLayer.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="System.Drawing.Common"><HintPath>$LIBS_W\System.Drawing.Common.dll</HintPath><Private>false</Private></Reference>
    $EXTRA
    <Compile Include="$HERE_W\OrderFlowBubbles.cs" />
    <Compile Include="$HERE_W\SignalCache.cs" />
    <Compile Include="$HERE_W\StackedImbalance.cs" />
    <Compile Include="$HERE_W\ExhaustionLogic.cs" />
    <Compile Include="$HERE_W\CellBigLogic.cs" />
    <Compile Include="$HERE_W\StopHuntLogic.cs" />
    <Compile Include="$HERE_W\RollingRobust.cs" />
  </ItemGroup>
</Project>
XML
dotnet build "$B_W\proj.csproj" -c Release -o "$B_W\out"
mkdir -p "$HERE/dist"
cp "$B/out/OrderFlowBubbles.dll" "$HERE/dist/OrderFlowBubbles.dll"
rm -rf "$B"
echo "==> $HERE/dist/OrderFlowBubbles.dll"
