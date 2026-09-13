# Deploy with the AWS CLI

Create skills and custom agents with `aws devops-agent create-asset`. This is
the Asset API surfaced through the CLI. Use it for scripted one-off creates or
to learn the API shape before automating with Bash or IaC.

Every command below takes your Agent Space ID. Export it once:

```bash
export AGENT_SPACE_ID="8f6187a7-0388-4926-8217-3a0fe32f757c"
export AWS_REGION="us-east-1"   # a Region where DevOps Agent is offered
```

---

## IAM permissions

The calling principal needs `aidevops:` permissions on your Agent Space. Replace
the account, Region, and Agent Space ID in the resource ARN.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aidevops:CreateAsset",
        "aidevops:GetAsset",
        "aidevops:UpdateAsset",
        "aidevops:DeleteAsset",
        "aidevops:ListAssets",
        "aidevops:ListAssetVersions",
        "aidevops:GetAssetContent",
        "aidevops:CreateAssetFile",
        "aidevops:GetAssetFile",
        "aidevops:UpdateAssetFile",
        "aidevops:DeleteAssetFile",
        "aidevops:ListAssetFiles"
      ],
      "Resource": "arn:aws:aidevops:us-east-1:111122223333:agentspace/8f6187a7-0388-4926-8217-3a0fe32f757c"
    },
    {
      "Effect": "Allow",
      "Action": "aidevops:ListAssetTypes",
      "Resource": "*"
    }
  ]
}
```

For a read-only principal, keep only the `Get*` and `List*` actions.

---

## Create a skill by importing from GitHub (recommended)

The service fetches the skill directory from this repo on GitHub, reads `name`
and `description` from the `SKILL.md` frontmatter, and keeps a sync link. Supply
only `agent_types` in metadata (uppercase enum - see the mapping table in
[../README.md](../README.md#two-things-that-trip-people-up)).

```bash
aws devops-agent create-asset \
  --agent-space-id "$AGENT_SPACE_ID" \
  --asset-type skill \
  --metadata '{ "agent_types": ["INCIDENT_RCA"] }' \
  --content '{"sourceUrl": {"url": "https://github.com/YOUR-ORG/YOUR-REPO/tree/main/skills/incident-management/blast-radius-assessment"}}'
```

Sync it later after you push changes:

```bash
aws devops-agent update-asset \
  --agent-space-id "$AGENT_SPACE_ID" \
  --asset-id "<assetId>" \
  --content '{"sourceUrl": {"url": "https://github.com/YOUR-ORG/YOUR-REPO/tree/main/skills/incident-management/blast-radius-assessment"}}'
```

---

## Create a skill from inline content (no GitHub)

Supply `name` and `description` in metadata for a single-file skill. Use this
when the repo is not on GitHub.

```bash
aws devops-agent create-asset \
  --agent-space-id "$AGENT_SPACE_ID" \
  --asset-type skill \
  --metadata '{
    "name": "blast-radius-assessment",
    "description": "Determines the full blast radius of an incident by mapping service dependencies. Use when an incident is confirmed and responders need the full scope of impact.",
    "agent_types": ["INCIDENT_RCA"]
  }' \
  --content '{ "file": { "path": "SKILL.md", "body": { "text": "# Blast Radius Assessment\n\nInstructions go here." } } }'
```

For a multi-file skill, base64-encode a zip of the skill directory and pass it
as `content.zip.zipFile` (max 6 MB). See
[Managing assets](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-managing-assets.html)
for the zip example.

---

## Create a custom agent

The system prompt is the agent's content file. `tools` and `skills` reference
tools and skill assets by identifier. The skills you list must already exist in
the Agent Space (create them first).

```bash
aws devops-agent create-asset \
  --agent-space-id "$AGENT_SPACE_ID" \
  --asset-type custom_agent \
  --metadata '{
    "name": "daily-infra-health-report",
    "tools": ["use_aws", "query_cloudwatch_metrics", "list_cloudwatch_alarms", "list_investigations"],
    "skills": ["operational-excellence-reviewer", "reliability-reviewer"]
  }' \
  --content "$(python ../../scripts/_asset_content.py ../../agents/01-infrastructure-health-report/system-prompt.md AGENT.md)"
```

`_asset_content.py` is a small helper (in this folder) that turns a system
prompt file into the `--content` JSON with correct escaping. You can also build
the JSON by hand: `{ "file": { "path": "AGENT.md", "body": { "text": "<prompt>" } } }`.

---

## Read, list, update, delete

```bash
# list every asset in the Agent Space
aws devops-agent list-assets --agent-space-id "$AGENT_SPACE_ID" --max-results 50

# get one asset
aws devops-agent get-asset --agent-space-id "$AGENT_SPACE_ID" --asset-id "<assetId>"

# change agent types without re-uploading content (PATCH semantics)
aws devops-agent update-asset --agent-space-id "$AGENT_SPACE_ID" \
  --asset-id "<assetId>" --metadata '{ "agent_types": ["GENERIC"] }'

# deactivate a skill (skills only) without deleting it
aws devops-agent update-asset --agent-space-id "$AGENT_SPACE_ID" \
  --asset-id "<assetId>" --metadata '{ "status": "INACTIVE" }'

# delete
aws devops-agent delete-asset --agent-space-id "$AGENT_SPACE_ID" --asset-id "<assetId>"
```

Triggers (scheduled runs) are not part of the Asset API. Set them in the Console
(see [../console/README.md](../console/README.md)) or with the
`AWS::DevOpsAgent::Trigger` resource in the
[CloudFormation](../cloudformation/README.md) option.

---

## Notes

- `status` (ACTIVE / INACTIVE, uppercase) applies to skills only.
- `agent_types` is an array; `GENERIC` cannot be combined with other values.
- `content.sourceUrl` is mutually exclusive with `content.file` and
  `content.zip` in a single request.
