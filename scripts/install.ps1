# hola-ai + engram installer (Windows, PowerShell 5+).
# Usage: .\scripts\install.ps1
param(
    [string]$Fork = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
    [string]$EngramVersion = "3.6.0",
    [switch]$CopySkills
)

$ErrorActionPreference = "Stop"
$ids = @("backlog", "story", "pair", "archive")
$home_ = $env:USERPROFILE
$engramDir = Join-Path $env:LOCALAPPDATA "engram"
$engramExe = Join-Path $engramDir "engram.exe"

function Say($m) { Write-Host $m }

# --- 1. Engram binary -------------------------------------------------------
if (Test-Path $engramExe) {
    Say "engram: already installed"
} else {
    Say "engram: installing $EngramVersion"
    New-Item -ItemType Directory -Force -Path $engramDir | Out-Null
    $asset = "engram_${EngramVersion}_windows_amd64.zip"
    $base = "https://github.com/Gentleman-Programming/engram/releases/download/v$EngramVersion"
    $zip = Join-Path $env:TEMP $asset
    Invoke-WebRequest -Uri "$base/$asset" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $engramDir -Force
    Remove-Item $zip
    Say "engram: installed at $engramExe"
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$engramDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$engramDir", "User")
    Say "engram: added $engramDir to the user PATH (restart the shell)"
}

# --- 2. Skills: junction (or copy with -CopySkills) -------------------------
$agentsRoot = Join-Path $home_ ".agents\skills"
New-Item -ItemType Directory -Force -Path $agentsRoot | Out-Null

$agentDirs = @(
    (Join-Path $home_ ".claude\skills"),
    (Join-Path $home_ ".gemini\skills"),
    (Join-Path $home_ ".continue\skills"),
    (Join-Path $home_ ".codeium\windsurf\skills"),
    (Join-Path $home_ ".kiro\skills"),
    (Join-Path $home_ ".config\devin\skills")
)

foreach ($id in $ids) {
    $src = Join-Path $Fork "skills\$id"
    if (-not (Test-Path $src)) { throw "skill $id missing in $Fork" }
    $dst = Join-Path $agentsRoot $id
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    if ($CopySkills) {
        Copy-Item $src $dst -Recurse
    } else {
        try { New-Item -ItemType Junction -Path $dst -Target $src | Out-Null }
        catch { Copy-Item $src $dst -Recurse; Say "skills: junction failed for $id, copied instead" }
    }
    foreach ($dir in $agentDirs) {
        if (Test-Path $dir) {
            $link = Join-Path $dir $id
            if (Test-Path $link) { Remove-Item $link -Recurse -Force }
            if ($CopySkills) { Copy-Item $src $link -Recurse }
            else {
                try { New-Item -ItemType Junction -Path $link -Target $src | Out-Null }
                catch { Copy-Item $src $link -Recurse }
            }
        }
    }
}
Say "skills: linked $($ids -join ', ')"

# --- 3. OpenCode commands ---------------------------------------------------
$cmdDir = Join-Path $home_ ".config\opencode\commands"
New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null
Copy-Item (Join-Path $Fork "commands\*.md") $cmdDir -Force
Say "commands: copied to $cmdDir"

# --- 4. MCP: print, never rewrite someone's config --------------------------
$engram = Join-Path $engramDir "engram.exe"
Say ""
Say "MCP servers (add once per agent):"
Say "  OpenCode -> ~/.config/opencode/opencode.json, under mcp.servers:"
Say "    `"engram`": { `"type`": `"local`", `"command`": [`"$($engram -replace '\\','/')`", `"mcp`", `"--tools=agent`"], `"disabled`": false }"
Say "  Claude Code -> claude mcp add --scope user engram -- `"$engram`" mcp --tools=agent"
Say "  Codex -> %USERPROFILE%\.codex\config.toml: [mcp_servers.engram] command = `"$($engram -replace '\\','/')`""
Say ""
Say "Restart the agent afterwards. Verify by using a tool in a NEW session."
Say "Engram sharing: git pull -> engram sync --import ; before pushing -> engram sync"
