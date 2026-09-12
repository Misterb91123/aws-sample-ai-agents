#!/usr/bin/env python3
"""Generate ready-to-paste Chat deploy commands for the custom agents.

AWS DevOps Agent imports a custom agent from a single Markdown system-prompt
file. It does NOT read agent-config.json, so the tools, skills, and trigger
defined there must be applied separately through Chat (or the Asset API). This
script turns each agent-config.json into a copy-paste block you can send to
Chat to create the agent, assign its tools and skills, and set its trigger.

Usage:
  python scripts/generate_deploy_commands.py                # all agents to stdout
  python scripts/generate_deploy_commands.py 01 02 17       # only matching agents
  python scripts/generate_deploy_commands.py --out FILE     # write to a file

The agent number/name filter matches against the agent directory name
(for example "01" matches "01-infrastructure-health-report").
"""

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(REPO_ROOT, "agents")


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_block(entry, config):
    name = config.get("name", entry)
    tools = ", ".join(config.get("tools", []))
    skills = ", ".join(config.get("skills", []))
    trigger = config.get("trigger", {})
    expression = trigger.get("expression", "")
    prompt_rel = "agents/%s/system-prompt.md" % entry

    lines = []
    lines.append("=== %s ===" % name)
    lines.append(
        'Create a custom agent named "%s" with these tools: %s.' % (name, tools)
    )
    if skills:
        lines.append("Assign these skills: %s." % skills)
    if expression:
        lines.append("Set a schedule trigger: %s." % expression)
    lines.append("Use the system prompt in %s." % prompt_rel)
    lines.append("")
    return "\n".join(lines)


def _matches(entry, filters):
    # Directory names look like "01-infrastructure-health-report". Split the
    # leading numeric id from the descriptive slug so a numeric filter matches
    # the exact agent number (01 matches 01, not 101 or 201) while a text
    # filter still matches anywhere in the slug.
    number, _, slug = entry.partition("-")
    for f in filters:
        if f.isdigit():
            if number == f:
                return True
        elif f in entry or f in slug:
            return True
    return False


def iter_agents(filters):
    for entry in sorted(os.listdir(AGENTS_DIR)):
        agent_dir = os.path.join(AGENTS_DIR, entry)
        if not os.path.isdir(agent_dir):
            continue
        if filters and not _matches(entry, filters):
            continue
        config_path = os.path.join(agent_dir, "agent-config.json")
        if not os.path.isfile(config_path):
            continue
        yield entry, read_json(config_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filters",
        nargs="*",
        help="Optional agent number/name filters (for example 01 02 cost).",
    )
    parser.add_argument(
        "--out",
        help="Write output to this file instead of stdout.",
    )
    args = parser.parse_args()

    if not os.path.isdir(AGENTS_DIR):
        print("agents directory not found", file=sys.stderr)
        return 1

    blocks = []
    count = 0
    for entry, config in iter_agents(args.filters):
        blocks.append(build_block(entry, config))
        count += 1

    output = "\n".join(blocks)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output)
        print("Wrote %d agent deploy command block(s) to %s" % (count, args.out))
    else:
        sys.stdout.write(output)
        print("Generated %d agent deploy command block(s)." % count, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
