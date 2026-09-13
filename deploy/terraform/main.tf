terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type        = string
  description = "A Region where AWS DevOps Agent is offered."
  default     = "us-east-1"
}

variable "agent_space_id" {
  type        = string
  description = "The UUID of the Agent Space that owns the assets."
}

variable "stack_name" {
  type        = string
  description = "Name for the CloudFormation stack Terraform manages."
  default     = "devops-agent-sample"
}

# The DevOps Agent resource types (AWS::DevOpsAgent::Asset and ::Trigger) are
# managed through a CloudFormation stack. This keeps the Terraform workflow
# (plan, apply, destroy, state) while relying on the same resource types the
# CloudFormation and CDK options use. The template body is the shared
# self-contained example in ../cloudformation/agent-stack.yaml.
resource "aws_cloudformation_stack" "devops_agent" {
  name          = var.stack_name
  template_body = file("${path.module}/../cloudformation/agent-stack.yaml")

  parameters = {
    AgentSpaceId = var.agent_space_id
  }

  # The template only creates DevOps Agent assets and triggers; no IAM.
  capabilities = []
}

output "skill_asset_id" {
  description = "Asset ID of the operational-excellence-reviewer skill."
  value       = aws_cloudformation_stack.devops_agent.outputs["SkillAssetId"]
}

output "agent_asset_id" {
  description = "Asset ID of the daily-infra-health-report custom agent."
  value       = aws_cloudformation_stack.devops_agent.outputs["AgentAssetId"]
}

output "agent_arn" {
  description = "ARN of the custom agent."
  value       = aws_cloudformation_stack.devops_agent.outputs["AgentArn"]
}
