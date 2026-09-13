#!/usr/bin/env python3
"""Validate the AWS DevOps Agent custom agents and skills collection.

Checks enforced:
- Pure ASCII across all .md, .json, .py, .ps1, .yml, .yaml, and .txt files
  (no em dashes, en dashes, curly quotes, ellipses, emojis, etc.).
- Every agent-config.json is valid JSON with the required fields.
- Every agent-config.json only references tools from the known DevOps Agent tool set.
- Every agent system-prompt.md contains the six required sections in order:
  Goal, Approach, Exception Handling, Data Validation, Constraints, Output.
- Every skill SKILL.md has YAML frontmatter with name, description, and a valid agent_type.
- Every skill referenced by an agent config actually exists on disk.

Version control and generated or third-party build output (.git, node_modules,
cdk.out, .terraform) are skipped so the checks only cover the repository's own
source.

Exit code 0 on success, 1 on any failure. Safe to run in CI.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(REPO_ROOT, "agents")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

REQUIRED_SECTIONS = [
    "## Goal",
    "## Approach",
    "## Exception Handling",
    "## Data Validation",
    "## Constraints",
    "## Output",
]

REQUIRED_CONFIG_FIELDS = ["name", "description", "tools", "skills", "trigger"]

# MCP tools exposed by AWS DevOps Agent Agent Spaces that the agents in this
# repository rely on. Tools are assigned to a custom agent through Chat or the
# Asset API; a name that is not in this set will silently fail to attach, so we
# reject unknown tool names at validation time. Extend this list if you add
# agents that use additional Agent Space tools.
KNOWN_TOOLS = {
    "use_aws",
    "query_cloudwatch_metrics",
    "query_cloudwatch_logs",
    "list_cloudwatch_alarms",
    "list_investigations",
    "use_kubectl",
}

# Agent types supported by AWS DevOps Agent Skills. A skill's agent_type
# frontmatter controls which agent types can load it. "Generic" applies to all
# agent types.
KNOWN_AGENT_TYPES = {
    "Generic",
    "On-demand",
    "Incident Triage",
    "Incident RCA",
    "Incident Mitigation",
    "Incident UI",
    "Evaluation",
    "Release testing",
}


def is_ascii(text):
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


# Directories that are not part of the repository's own source and must not be
# validated: version control, and third-party or generated build output from the
# deploy/ tooling (for example a contributor running `npm install` under
# deploy/cdk creates node_modules with non-ASCII third-party docs).
EXCLUDED_DIRS = {".git", "node_modules", "cdk.out", ".terraform"}


def iter_files(root, suffixes):
    for base, dirs, files in os.walk(root):
        # Prune excluded directories in place so os.walk does not descend into
        # them (this also speeds up the walk considerably).
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name.endswith(suffixes):
                yield os.path.join(base, name)


def rel(path):
    return os.path.relpath(path, REPO_ROOT)


ASCII_SUFFIXES = (".md", ".json", ".py", ".ps1", ".yml", ".yaml", ".txt")


def first_non_ascii(line):
    for col, ch in enumerate(line, start=1):
        if ord(ch) > 127:
            return col, ch
    return None


def check_ascii(errors):
    seen = set()
    for path in iter_files(REPO_ROOT, ASCII_SUFFIXES):
        if os.sep + ".git" + os.sep in path:
            continue
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        try:
            content = read(path)
        except (OSError, UnicodeDecodeError) as exc:
            errors.append("cannot read %s: %s" % (rel(path), exc))
            continue
        if not is_ascii(content):
            for i, line in enumerate(content.splitlines(), start=1):
                found = first_non_ascii(line)
                if found:
                    col, ch = found
                    errors.append(
                        "non-ASCII in %s line %d col %d: U+%04X"
                        % (rel(path), i, col, ord(ch))
                    )
                    break


def collect_skill_names():
    names = set()
    if not os.path.isdir(SKILLS_DIR):
        return names
    for domain in os.listdir(SKILLS_DIR):
        domain_path = os.path.join(SKILLS_DIR, domain)
        if not os.path.isdir(domain_path):
            continue
        for skill in os.listdir(domain_path):
            if os.path.isfile(os.path.join(domain_path, skill, "SKILL.md")):
                names.add(skill)
    return names


def check_agents(errors, skill_names):
    if not os.path.isdir(AGENTS_DIR):
        errors.append("agents directory not found")
        return 0
    count = 0
    for entry in sorted(os.listdir(AGENTS_DIR)):
        agent_dir = os.path.join(AGENTS_DIR, entry)
        if not os.path.isdir(agent_dir):
            continue
        count += 1
        prompt_path = os.path.join(agent_dir, "system-prompt.md")
        config_path = os.path.join(agent_dir, "agent-config.json")

        if not os.path.isfile(prompt_path):
            errors.append("%s: missing system-prompt.md" % entry)
        else:
            prompt = read(prompt_path)
            last = -1
            for section in REQUIRED_SECTIONS:
                idx = prompt.find(section)
                if idx == -1:
                    errors.append("%s: missing section %s" % (entry, section))
                elif idx < last:
                    errors.append("%s: section %s out of order" % (entry, section))
                else:
                    last = idx

        if not os.path.isfile(config_path):
            errors.append("%s: missing agent-config.json" % entry)
            continue
        try:
            config = json.loads(read(config_path))
        except json.JSONDecodeError as exc:
            errors.append("%s: invalid JSON (%s)" % (entry, exc))
            continue
        for field in REQUIRED_CONFIG_FIELDS:
            if field not in config:
                errors.append("%s: config missing field '%s'" % (entry, field))
        tools = config.get("tools", [])
        if not tools:
            errors.append("%s: config has no tools" % entry)
        for tool in tools:
            if tool not in KNOWN_TOOLS:
                errors.append(
                    "%s: references unknown tool '%s' (not in the DevOps Agent tool set)"
                    % (entry, tool)
                )
        for skill in config.get("skills", []):
            if skill not in skill_names:
                errors.append("%s: references unknown skill '%s'" % (entry, skill))
    return count


def check_skills(errors):
    if not os.path.isdir(SKILLS_DIR):
        errors.append("skills directory not found")
        return 0
    count = 0
    for path in iter_files(SKILLS_DIR, ("SKILL.md",)):
        count += 1
        content = read(path)
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            errors.append("%s: missing opening frontmatter '---'" % rel(path))
            continue
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            errors.append("%s: missing closing frontmatter '---'" % rel(path))
            continue
        block = "\n".join(lines[1:end])
        if "name:" not in block:
            errors.append("%s: frontmatter missing 'name'" % rel(path))
        if "description:" not in block:
            errors.append("%s: frontmatter missing 'description'" % rel(path))
        agent_type = None
        for line in lines[1:end]:
            stripped = line.strip()
            if stripped.startswith("agent_type:"):
                agent_type = stripped[len("agent_type:"):].strip().strip('"').strip("'")
                break
        if agent_type is None:
            errors.append("%s: frontmatter missing 'agent_type'" % rel(path))
        elif agent_type not in KNOWN_AGENT_TYPES:
            errors.append(
                "%s: invalid agent_type '%s' (expected one of: %s)"
                % (rel(path), agent_type, ", ".join(sorted(KNOWN_AGENT_TYPES)))
            )
    return count


def main():
    errors = []
    check_ascii(errors)
    skill_names = collect_skill_names()
    agent_count = check_agents(errors, skill_names)
    skill_count = check_skills(errors)

    print("Agents checked: %d" % agent_count)
    print("Skills checked: %d" % skill_count)

    if errors:
        print("")
        print("VALIDATION FAILED with %d issue(s):" % len(errors))
        for err in errors:
            print("  - %s" % err)
        return 1

    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
