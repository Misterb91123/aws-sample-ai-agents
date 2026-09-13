import * as fs from "fs";
import * as path from "path";
import { CfnResource, Stack, StackProps, CfnOutput } from "aws-cdk-lib";
import { Construct } from "constructs";

/**
 * Maps a SKILL.md agent_type (Console label) to the Asset API enum value.
 */
const AGENT_TYPE_MAP: Record<string, string> = {
  Generic: "GENERIC",
  "On-demand": "CHAT",
  "Incident Triage": "INCIDENT_TRIAGE",
  "Incident RCA": "INCIDENT_RCA",
  "Incident Mitigation": "INCIDENT_MITIGATION",
  "Incident UI": "INCIDENT_UI",
  Evaluation: "PREVENTION",
  "Release testing": "RELEASE_TESTING",
};

/** Repository root, two levels up from deploy/cdk. */
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");

interface AgentConfig {
  name: string;
  tools: string[];
  skills: string[];
  trigger?: { expression?: string };
}

/** Read agent_type from SKILL.md frontmatter and map to the API enum. */
function readSkillAgentType(skillMd: string): string {
  const text = fs.readFileSync(skillMd, "utf8");
  const match = text.match(/^agent_type:\s*"?([^"\n]*)"?\s*$/m);
  const label = match ? match[1].trim() : "Generic";
  return AGENT_TYPE_MAP[label] ?? "GENERIC";
}

/** Find every skill directory that contains a SKILL.md. */
function findSkillDirs(skillsRoot: string): string[] {
  const result: string[] = [];
  for (const domain of fs.readdirSync(skillsRoot)) {
    const domainPath = path.join(skillsRoot, domain);
    if (!fs.statSync(domainPath).isDirectory()) continue;
    for (const skill of fs.readdirSync(domainPath)) {
      const skillPath = path.join(domainPath, skill);
      if (
        fs.statSync(skillPath).isDirectory() &&
        fs.existsSync(path.join(skillPath, "SKILL.md"))
      ) {
        result.push(skillPath);
      }
    }
  }
  return result;
}

/** A valid CloudFormation logical id from an arbitrary name. */
function logicalId(prefix: string, name: string): string {
  const clean = name.replace(/[^a-zA-Z0-9]/g, "");
  return `${prefix}${clean.charAt(0).toUpperCase()}${clean.slice(1)}`;
}

export interface DevOpsAgentStackProps extends StackProps {
  /** The Agent Space UUID that owns the assets. */
  readonly agentSpaceId: string;
  /**
   * Optional list of agent directory names (for example
   * "01-infrastructure-health-report") to deploy. Defaults to all agents.
   */
  readonly agentDirs?: string[];
}

/**
 * Creates DevOps Agent skill and custom_agent assets plus schedule triggers
 * from the repository's own skills/ and agents/ files, using the
 * AWS::DevOpsAgent::Asset and AWS::DevOpsAgent::Trigger resource types.
 */
export class DevOpsAgentStack extends Stack {
  constructor(scope: Construct, id: string, props: DevOpsAgentStackProps) {
    super(scope, id, props);

    const { agentSpaceId } = props;

    // --- skills -----------------------------------------------------------
    const skillResourceByName = new Map<string, CfnResource>();
    const skillsRoot = path.join(REPO_ROOT, "skills");
    for (const skillDir of findSkillDirs(skillsRoot)) {
      const skillMd = path.join(skillDir, "SKILL.md");
      const name = path.basename(skillDir);
      const agentType = readSkillAgentType(skillMd);
      const content = fs.readFileSync(skillMd, "utf8");

      // The service reads name and description from the SKILL.md frontmatter,
      // so metadata only needs agent_types.
      const skill = new CfnResource(this, logicalId("Skill", name), {
        type: "AWS::DevOpsAgent::Asset",
        properties: {
          AgentSpaceId: agentSpaceId,
          AssetType: "skill",
          Metadata: { agent_types: [agentType] },
          Files: [{ Path: "SKILL.md", ContentText: content }],
        },
      });
      skillResourceByName.set(name, skill);
    }

    // --- agents (and triggers) -------------------------------------------
    const agentsRoot = path.join(REPO_ROOT, "agents");
    const agentDirs =
      props.agentDirs ??
      fs
        .readdirSync(agentsRoot)
        .filter((d) => fs.statSync(path.join(agentsRoot, d)).isDirectory());

    for (const dir of agentDirs) {
      const agentDir = path.join(agentsRoot, dir);
      const configPath = path.join(agentDir, "agent-config.json");
      const promptPath = path.join(agentDir, "system-prompt.md");
      if (!fs.existsSync(configPath) || !fs.existsSync(promptPath)) continue;

      const config: AgentConfig = JSON.parse(
        fs.readFileSync(configPath, "utf8")
      );
      const prompt = fs.readFileSync(promptPath, "utf8");

      const agent = new CfnResource(this, logicalId("Agent", config.name), {
        type: "AWS::DevOpsAgent::Asset",
        properties: {
          AgentSpaceId: agentSpaceId,
          AssetType: "custom_agent",
          Metadata: {
            name: config.name,
            tools: config.tools ?? [],
            skills: config.skills ?? [],
          },
          Files: [{ Path: "AGENT.md", ContentText: prompt }],
        },
      });

      // Skills are referenced by name; make the agent depend on those skills.
      for (const skillName of config.skills ?? []) {
        const skillRes = skillResourceByName.get(skillName);
        if (skillRes) {
          agent.addDependency(skillRes);
        }
      }

      // Schedule trigger from agent-config.json (if present).
      const expression = config.trigger?.expression;
      if (expression) {
        new CfnResource(this, logicalId("Trigger", config.name), {
          type: "AWS::DevOpsAgent::Trigger",
          properties: {
            AgentSpaceId: agentSpaceId,
            Type: "TIME_BASED",
            Condition: { Schedule: { Expression: expression } },
            Action: {
              actionType: "create:task",
              task: { agent: `custom:${agent.getAtt("AssetId")}` },
            },
            Status: "Active",
          },
        });
      }

      new CfnOutput(this, logicalId("Out", config.name), {
        value: agent.getAtt("AssetId").toString(),
        description: `Asset ID of the ${config.name} custom agent`,
      });
    }
  }
}
