#!/usr/bin/env bash
#
# End-to-end deploy of the DevOps Agent skills and custom agents via the
# Asset API (aws devops-agent). Skills are imported from GitHub by URL so they
# keep a sync link; custom agents are created with their system prompt inline
# and their tools and skills attached from agent-config.json.
#
# Requirements: bash, aws CLI v2 (with the devops-agent service), jq, python3.
#
# Usage:
#   export AGENT_SPACE_ID=8f6187a7-0388-4926-8217-3a0fe32f757c
#   export AWS_REGION=us-east-1
#   export REPO_BASE=https://github.com/YOUR-ORG/YOUR-REPO/tree/main
#   ./deploy.sh                 # deploy all skills and all agents
#   ./deploy.sh --skills-only   # deploy only skills
#   ./deploy.sh --agents-only   # deploy only agents (skills must already exist)
#   ./deploy.sh --agents 01 02  # deploy only the named agents (by dir prefix)
#   ./deploy.sh --dry-run       # print what would be done, call nothing
#
set -euo pipefail

# --- resolve repo root (this script lives in deploy/bash) -------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# --- config -----------------------------------------------------------------
: "${AGENT_SPACE_ID:?set AGENT_SPACE_ID to your Agent Space UUID}"
: "${REPO_BASE:?set REPO_BASE to https://github.com/ORG/REPO/tree/BRANCH}"
AWS_REGION="${AWS_REGION:-us-east-1}"

DO_SKILLS=1
DO_AGENTS=1
DRY_RUN=0
AGENT_FILTER=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skills-only) DO_AGENTS=0; shift ;;
    --agents-only) DO_SKILLS=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --agents) shift; while [[ $# -gt 0 && "$1" != --* ]]; do AGENT_FILTER+=("$1"); shift; done ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# Map the SKILL.md agent_type (Console label) to the API enum value.
map_agent_type() {
  case "$1" in
    "Generic") echo "GENERIC" ;;
    "On-demand") echo "CHAT" ;;
    "Incident Triage") echo "INCIDENT_TRIAGE" ;;
    "Incident RCA") echo "INCIDENT_RCA" ;;
    "Incident Mitigation") echo "INCIDENT_MITIGATION" ;;
    "Incident UI") echo "INCIDENT_UI" ;;
    "Evaluation") echo "PREVENTION" ;;
    "Release testing") echo "RELEASE_TESTING" ;;
    *) echo "GENERIC" ;;
  esac
}

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'DRY-RUN: %s\n' "$*"
  else
    "$@"
  fi
}

# --- skills -----------------------------------------------------------------
deploy_skills() {
  echo "== Importing skills from $REPO_BASE =="
  # every skill directory that contains a SKILL.md
  while IFS= read -r skill_md; do
    skill_dir="$(dirname "$skill_md")"
    rel="${skill_dir#"$REPO_ROOT"/}"
    # read agent_type from frontmatter (first agent_type: line)
    label="$(grep -m1 '^agent_type:' "$skill_md" | sed -E 's/^agent_type:[[:space:]]*"?([^"]*)"?[[:space:]]*$/\1/')"
    api_type="$(map_agent_type "$label")"
    url="$REPO_BASE/$rel"
    echo "-> $rel  [$label -> $api_type]"
    run aws devops-agent create-asset \
      --region "$AWS_REGION" \
      --agent-space-id "$AGENT_SPACE_ID" \
      --asset-type skill \
      --metadata "{\"agent_types\":[\"$api_type\"]}" \
      --content "{\"sourceUrl\":{\"url\":\"$url\"}}"
  done < <(find "$REPO_ROOT/skills" -name SKILL.md | sort)
}

# --- agents -----------------------------------------------------------------
agent_selected() {
  local entry="$1"
  [[ ${#AGENT_FILTER[@]} -eq 0 ]] && return 0
  local f
  for f in "${AGENT_FILTER[@]}"; do
    [[ "$entry" == "$f"* || "$entry" == *"$f"* ]] && return 0
  done
  return 1
}

deploy_agents() {
  echo "== Creating custom agents =="
  local dir cfg name tools skills entry
  for dir in "$REPO_ROOT"/agents/*/; do
    entry="$(basename "$dir")"
    agent_selected "$entry" || continue
    cfg="$dir/agent-config.json"
    [[ -f "$cfg" ]] || continue
    name="$(jq -r '.name' "$cfg")"
    tools="$(jq -c '.tools' "$cfg")"
    skills="$(jq -c '.skills' "$cfg")"
    local metadata
    metadata="$(jq -nc --arg n "$name" --argjson t "$tools" --argjson s "$skills" \
      '{name:$n, tools:$t, skills:$s}')"
    local content
    content="$(python3 "$REPO_ROOT/scripts/_asset_content.py" "$dir/system-prompt.md" AGENT.md)"
    echo "-> $name"
    run aws devops-agent create-asset \
      --region "$AWS_REGION" \
      --agent-space-id "$AGENT_SPACE_ID" \
      --asset-type custom_agent \
      --metadata "$metadata" \
      --content "$content"
  done
  echo
  echo "Note: schedule triggers are not part of the Asset API. Set them in the"
  echo "Console, or use the CloudFormation option to create AWS::DevOpsAgent::Trigger"
  echo "resources. Each agent's recommended expression is in its agent-config.json."
}

[[ "$DO_SKILLS" -eq 1 ]] && deploy_skills
[[ "$DO_AGENTS" -eq 1 ]] && deploy_agents
echo "Done."
