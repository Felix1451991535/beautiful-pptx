#!/usr/bin/env bash
# Strict Open XML SDK validation for pptx/docx/xlsx:  scripts/oxv.sh file...
# First run builds tools/oxv (needs .NET 8 SDK). Exit code 1 if any errors.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
[ -d "$HOME/.dotnet" ] && export PATH="$HOME/.dotnet:$PATH"
DLL="$DIR/tools/oxv/bin/Release/net8.0/oxv.dll"
if [ ! -f "$DLL" ]; then
  dotnet build "$DIR/tools/oxv/oxv.csproj" -c Release -o "$DIR/tools/oxv/bin/Release/net8.0" >&2
fi
exec dotnet "$DLL" "$@"
