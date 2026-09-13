#!/usr/bin/env node
import { App } from "aws-cdk-lib";
import { DevOpsAgentStack } from "../lib/devops-agent-stack";

const app = new App();

// The Agent Space UUID is required. Pass it via context:
//   cdk deploy -c agentSpaceId=8f6187a7-0388-4926-8217-3a0fe32f757c
// or set DEVOPS_AGENT_SPACE_ID in the environment.
const agentSpaceId =
  app.node.tryGetContext("agentSpaceId") ??
  process.env.DEVOPS_AGENT_SPACE_ID;

if (!agentSpaceId) {
  throw new Error(
    "Set the Agent Space ID: cdk deploy -c agentSpaceId=<uuid> " +
      "(or export DEVOPS_AGENT_SPACE_ID)."
  );
}

// Optional: limit to specific agent directories, comma-separated:
//   cdk deploy -c agentDirs=01-infrastructure-health-report,02-cost-anomaly-detector
const agentDirsCtx: string | undefined = app.node.tryGetContext("agentDirs");
const agentDirs = agentDirsCtx
  ? agentDirsCtx.split(",").map((s) => s.trim()).filter(Boolean)
  : undefined;

new DevOpsAgentStack(app, "DevOpsAgentStack", {
  agentSpaceId,
  agentDirs,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
