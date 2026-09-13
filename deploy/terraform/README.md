# Deploy with Terraform

Deploy the DevOps Agent skill, custom agent, and trigger through Terraform.

The DevOps Agent resource types (`AWS::DevOpsAgent::Asset` and
`AWS::DevOpsAgent::Trigger`) are managed here via an `aws_cloudformation_stack`
that wraps the shared template in
[../cloudformation/agent-stack.yaml](../cloudformation/agent-stack.yaml). You
get the full Terraform workflow (plan, apply, destroy, remote state) while
using the same resource types as the CloudFormation and CDK options. This
approach works today regardless of whether the AWS or AWSCC Terraform providers
have first-class support for these new resource types (see
[Alternative](#alternative-awscc-provider) below).

---

## Layout

```
deploy/terraform/
  main.tf                       Provider, variables, the wrapping stack, outputs
  terraform.tfvars.example      Copy to terraform.tfvars and edit
  README.md
```

---

## Prerequisites

- Terraform >= 1.5.0 and AWS credentials with `aidevops:` permissions on the
  Agent Space (see [../aws-cli/README.md](../aws-cli/README.md#iam-permissions))
  plus CloudFormation permissions to create the stack.
- Deploy into a Region where AWS DevOps Agent is offered.

---

## Deploy

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: set agent_space_id (and region if needed)

terraform init
terraform plan
terraform apply
```

Outputs expose the created skill and agent asset IDs and the agent ARN.

Tear down with `terraform destroy`.

---

## Scaling to the full repository

The wrapped template is the self-contained single-agent example. To manage more
assets, extend
[../cloudformation/agent-stack.yaml](../cloudformation/agent-stack.yaml) with
additional `AWS::DevOpsAgent::Asset` and `AWS::DevOpsAgent::Trigger` resources
(or generate it from the repo files), and Terraform will apply the larger stack
unchanged. If you prefer to generate resources from the repo files in code
rather than YAML, the [CDK](../cdk/README.md) option does exactly that.

---

## Alternative: AWSCC provider

If you prefer native Terraform resources over a wrapped stack, the AWS Cloud
Control provider ([`hashicorp/awscc`](https://registry.terraform.io/providers/hashicorp/awscc/latest))
exposes CloudFormation resource types directly through the Cloud Control API. If
and when it surfaces `awscc_devops_agent_asset` and
`awscc_devops_agent_trigger`, you can declare them natively, for example:

```hcl
# Illustrative - confirm the resource name and schema in the awscc provider docs.
resource "awscc_devops_agent_asset" "skill" {
  agent_space_id = var.agent_space_id
  asset_type     = "skill"
  metadata       = jsonencode({ agent_types = ["PREVENTION"] })
  files = [{
    path         = "SKILL.md"
    content_text = file("${path.module}/skill.md")
  }]
}
```

Until you have confirmed that support in your provider version, the
`aws_cloudformation_stack` approach in `main.tf` is the reliable path.
