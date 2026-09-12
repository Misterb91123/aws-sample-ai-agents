# Validate the AWS DevOps Agent custom agents and skills collection.
#
# Checks: pure ASCII across .md and .json; valid agent-config.json with required
# fields; six required system-prompt sections in order; skill frontmatter with
# name and description; and that agent skill references resolve to a real skill.
#
# Usage (from repo root):  pwsh -File scripts/validate.ps1
# Exit code 0 on success, 1 on any failure.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$agentsDir = Join-Path $root 'agents'
$skillsDir = Join-Path $root 'skills'
$errors = New-Object System.Collections.Generic.List[string]

$requiredSections = @('## Goal', '## Approach', '## Exception Handling', '## Data Validation', '## Constraints', '## Output')
$requiredFields = @('name', 'description', 'tools', 'skills', 'trigger')

function Add-Err([string]$m) { $script:errors.Add($m) }
function RelPath([string]$p) { return $p.Substring($root.Length).TrimStart('\', '/') }

# ASCII check across all md and json
Get-ChildItem -Path $root -Recurse -Include '*.md', '*.json' -File | ForEach-Object {
    $c = Get-Content -Raw -LiteralPath $_.FullName
    if ($c -and ($c -match '[^\x00-\x7F]')) { Add-Err ("non-ASCII in {0}" -f (RelPath $_.FullName)) }
}

# Collect skill names
$skillNames = @{}
if (Test-Path $skillsDir) {
    Get-ChildItem -Path $skillsDir -Directory | ForEach-Object {
        Get-ChildItem -Path $_.FullName -Directory | ForEach-Object {
            if (Test-Path (Join-Path $_.FullName 'SKILL.md')) { $skillNames[$_.Name] = $true }
        }
    }
}

# Agents
$agentCount = 0
if (Test-Path $agentsDir) {
    Get-ChildItem -Path $agentsDir -Directory | Sort-Object Name | ForEach-Object {
        $agentCount++
        $name = $_.Name
        $sp = Join-Path $_.FullName 'system-prompt.md'
        $cfg = Join-Path $_.FullName 'agent-config.json'
        if (-not (Test-Path $sp)) { Add-Err "${name}: missing system-prompt.md" }
        else {
            $prompt = Get-Content -Raw -LiteralPath $sp
            $last = -1
            foreach ($section in $requiredSections) {
                $idx = $prompt.IndexOf($section)
                if ($idx -lt 0) { Add-Err "${name}: missing section $section" }
                elseif ($idx -lt $last) { Add-Err "${name}: section $section out of order" }
                else { $last = $idx }
            }
        }
        if (-not (Test-Path $cfg)) { Add-Err "${name}: missing agent-config.json" }
        else {
            try {
                $config = Get-Content -Raw -LiteralPath $cfg | ConvertFrom-Json
                foreach ($f in $requiredFields) {
                    if (-not ($config.PSObject.Properties.Name -contains $f)) { Add-Err "${name}: config missing field '$f'" }
                }
                foreach ($s in @($config.skills)) {
                    if ($s -and -not $skillNames.ContainsKey($s)) { Add-Err "${name}: references unknown skill '$s'" }
                }
            }
            catch { Add-Err "${name}: invalid JSON" }
        }
    }
}
else { Add-Err 'agents directory not found' }

# Skills
$skillCount = 0
if (Test-Path $skillsDir) {
    Get-ChildItem -Path $skillsDir -Recurse -Filter 'SKILL.md' | ForEach-Object {
        $skillCount++
        $lines = Get-Content -LiteralPath $_.FullName
        if ($lines.Count -eq 0 -or $lines[0].Trim() -ne '---') { Add-Err ("{0}: missing opening frontmatter" -f (RelPath $_.FullName)); return }
        $end = -1
        for ($i = 1; $i -lt $lines.Count; $i++) { if ($lines[$i].Trim() -eq '---') { $end = $i; break } }
        if ($end -lt 0) { Add-Err ("{0}: missing closing frontmatter" -f (RelPath $_.FullName)); return }
        $block = ($lines[1..($end - 1)] -join "`n")
        if ($block -notmatch 'name:') { Add-Err ("{0}: frontmatter missing name" -f (RelPath $_.FullName)) }
        if ($block -notmatch 'description:') { Add-Err ("{0}: frontmatter missing description" -f (RelPath $_.FullName)) }
    }
}
else { Add-Err 'skills directory not found' }

Write-Output "Agents checked: $agentCount"
Write-Output "Skills checked: $skillCount"

if ($errors.Count -gt 0) {
    Write-Output ""
    Write-Output ("VALIDATION FAILED with {0} issue(s):" -f $errors.Count)
    $errors | ForEach-Object { Write-Output "  - $_" }
    exit 1
}
Write-Output "VALIDATION PASSED"
exit 0
