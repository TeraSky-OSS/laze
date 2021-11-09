# LAZE - Landing Zone as Code

This project is meant to replace AWS Control Tower as the tool to provision AWS Landing Zone according to best practices.

## Capabilities

| Name | AWS Control Tower | LAZE |
|------|-------------------|------|
| Create an organization | :heavy_check_mark: | :heavy_check_mark: |
| Set account alias for management (root) account | :x: | :heavy_check_mark: |
| Set global tags that will be assigned to all (supported) resources | :x: | :heavy_check_mark: |
| Create management accounts (Audit and Log Archive) | :heavy_check_mark: | :heavy_check_mark: (WIP) |
| Deploy management "roles" on a single account | :x: | :heavy_check_mark: |
| Create custom organizational policies (SCPs, tag policies, etc.) | :heavy_check_mark: (only SCPs) | :heavy_check_mark: |
| Create custom organizational units (OUs) | :heavy_check_mark: | :heavy_check_mark: |
| Create nested organizational units (OUs) | :x: | :heavy_check_mark: |
| Attach policies to OUs | :heavy_check_mark: | :heavy_check_mark: |
| Create custom AWS accounts in specified OUs | :heavy_check_mark: | :heavy_check_mark: |
| Attach policies to AWS accounts | :heavy_check_mark: | :heavy_check_mark: |
| Create network resources (VPC, subnetc, etc.) in AWS accounts | :heavy_check_mark: (very basic) | :heavy_check_mark: |
| Provision custom Terraform modules (HCL) in AWS accounts | :x: | :heavy_check_mark: |
| Deploy Transit Gateway | :x: | :x: (planned) |
| Deploy SSO with custom configurations | :x: | :x: (planned) |

## Configuration File

The deployment of the organization and all resources is based on a YAML configuration file that should be provided by the customer.

The following are the accepted attributes for the YAML configuration file:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `region` | AWS Region to deploy all resources in | `string` | `us-east-1` | no |
| `aws_profile` | AWS profile name as set in the shared credentials file | `string` | `default` | no |
| `create_organization` | Whether an organization should be created, or use an existing one | `boolean` | `true` | no |
| `root_account_alias` | IAM alias for the root account | `string` | `""` | no |
| `global_tags` | Map of tags to apply to all resources (key-value pairs) | `object` | `{}` | no |
| `policies` | List of organization policies blocks | `list(object)` | `[]` | no |
| `policies.name` | Name of the policy | `string` | n/a | yes |
| `policies.type` | Type of the policy (`SERVICE_CONTROL_POLICY` / `TAG_POLICY` / `BACKUP_POLICY` / `AISERVICES_OPT_OUT_POLICY`) | `string` | n/a | yes |
| `policies.content_inline` | Inline policy content in a JSON format | `string` | n/a | yes (if `content_from_file` is not specified) |
| `policies.content_from_file` | Path to a JSON file containing the policy content | `string` | n/a | yes (if `content_inline` is not specified) |
| `organizational_units` | List of organizational units | `list(object)` | `[]` | no |
| `organizational_units.name` | Name of the organizational unit | `string` | n/a | yes |
| `organizational_units.policies` | List of organization policies names to attach to the organizational unit | `list(string)` | `[]` | no |
| `organizational_units.parent_ou` | Name of the parent organizational unit | `string` | `""` = root OU | no |
| `accounts` | List of organization accounts | `list(object)` | `[]` | no |
| `accounts.name` | Name of the account | `string` | n/a | yes |
| `accounts.email` | Email of the account | `string` | n/a | yes |
| `accounts.ou` | Name of the OU to place the account in | `string` | n/a | yes |
| `accounts.roles` | List of roles for the account (Supports: `audit`, `log_archive` or `standard`) | `list(string)` | `[]` | no |
| `accounts.policies` | List of organization policies names to attach to the account | `list(string)` | `[]` | no |
| `accounts.network` | Network configuration block for the account | `object` | `{}` | no |
| `accounts.network.create` | Whether to create network resoruces in the account | `boolean` | `true` | no |
| `accounts.network.name` | Name of the desired VPC (also prefix for subnets and other network resoruces) | `string` | n/a | yes (if `create` == `true`) |
| `accounts.network.vpc_cidr` | CIDR of the desired VPC | `string` | n/a | yes (if `create` == `true`) |
| `accounts.network.public_subnets` | List of CIDRs for the public subnets | `list(string)` | `[]` | no |
| `accounts.network.private_subnets` | List of CIDRs for the private subnets | `list(string)` | `[]` | no |
| `tf_modules` | List of Terraform modules that will be provisioned automatically on the created accounts | `list(object)` | `[]` | no |
| `tf_modules.name` | Logical name (alias) of the Terraform module (HCL) to deploy | `string` | n/a | yes |
| `tf_modules.source` | Source of the Terraform module (HCL) to deploy (registry/git repo/local path) | `string` | n/a | yes |
| `tf_modules.version` | Version of the Terraform module (relevant only when source is from Terraform Registry) | `string` | "latest" | no |
| `tf_modules.variables` | Map of variables (with values) to pass to the module | `object` | `{}` | no |
| `tf_modules.accounts` | List of AWS account names to provision the modules on | `list(string)` | n/a | yes |

The following is the YAML file that should be provided, with explanation on each of the attributes:

```yaml
# (Optional) AWS Region to deploy all resources in (default: us-east-1)
region: us-east-1
# (Optional) AWS profile name as set in the shared credentials file (default: default)
aws_profile: default
# (Optional) Whether an organization should be created, or use an existing one (default: true)
create_organization: true
# (Optional) IAM alias for the root account (default: "")
root_account_alias: terasky-laze-mgmt

# (Optional) Map of tags to apply to all resources (key-value pairs) (default: {})
# Example:
#   Environment: test
#   Owner: Daniel Vaknin
global_tags: {}

# (Optional) List of organization policies blocks (default: [])
# Example policy (inline):
#   # (Required) Name of the policy
# - name: example_scp_inline
#   # (Required) Type of the policy (SERVICE_CONTROL_POLICY / TAG_POLICY / BACKUP_POLICY / AISERVICES_OPT_OUT_POLICY)
#   type: SERVICE_CONTROL_POLICY
#   # (Optional) Inline policy content in a JSON format (required if "content_from_file" is not specified)
#   content_inline: |
#     {
#       "Version": "2012-10-17",
#       "Statement": {
#         "Effect": "Allow",
#         "Action": "*",
#         "Resource": "*"
#       }
#     }
# Example policy (from file):
#   # (Required) Name of the policy
# - name: scp_y
#   # (Required) Type of the policy (SERVICE_CONTROL_POLICY / TAG_POLICY / BACKUP_POLICY / AISERVICES_OPT_OUT_POLICY)
#   type: SERVICE_CONTROL_POLICY
#   # (Optional) Path to a JSON file containing the policy content (required if "content_inline" is not specified)
#   content_from_file: allow-all-policy.json
policies: []

# (Optional) List of organizational units (default: [])
# Example OU:
#   # (Required) Name of the organizational unit
# - name: prod
#   # (Optional) List of organization policies names to attach to the organizational unit (default: [])
#   policies:
#     - example_scp_inline
#   # (Optional) Name of the parent organizational unit (default: "" = root OU)
#   parent_ou: prod_parent
organizational_units: []

# (Optional) List of organization accounts (default: [])
# Example of account definition:
#   # (Required) Name of the account
# - name: TeraSky Laze Project A
#   # (Required) Email of the account
#   email: aws-project-laze-project-a@terasky.com
#   # (Required) Name of the OU to place the account in
#   ou: prod
#   # (Optional) List of roles for the account (Supports: `audit`, `log_archive` or `standard`)
#   roles:
#     - audit
#   # (Optional) List of organization policies names to attach to the account (default: [])
#   policies:
#     - example_scp_inline
#   # (Optional) Network configuration block for the account (default: {})
#   network:
#     # (Required) Whether to create network resoruces in the account
#     create: true
#     # (Required) Name of the desired VPC (also prefix for subnets and other network resoruces) (required if create == true)
#     name: laze-vpc
#     # (Required) CIDR of the desired VPC (required if create == true)
#     vpc_cidr: 20.0.0.0/16
#     # (Optional) List of CIDRs for the public subnets (default: [])
#     public_subnets: [20.0.1.0/24, 20.0.2.0/24, 20.0.3.0/24]
#     # (Optional) List of CIDRs for the private subnets (default: [])
#     private_subnets: [20.0.101.0/24, 20.0.102.0/24, 20.0.103.0/24]
accounts: []

# (Optional) List of Terraform modules that will be provisioned automatically on the created accounts (default: [])
# Example of resource definition:
#   # (Required) Logical name (alias) of the Terraform module (HCL) to deploy
# - name: aws-vpc
#   # (Required) Source of the Terraform module (HCL) to deploy (registry/git repo/local path)
#   source: terraform-aws-modules/vpc/aws
#   # (Optional) Version of the Terraform module (relevant only when source if from Terraform Registry) (default: "latest")
#   version: 3.7.0
#   # (Optional) Map of variables (with values) to pass to the module (default: {})
#   variables:
#     name: my-vpc
#     cidr: 10.0.0.0/16
#     azs: [eu-west-1a, eu-west-1b, eu-west-1c]
#     public_subnets: [10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24]
#   # (Required) List of AWS account names to provision the modules to
#   accounts:
#     - TeraSky Laze Project A
#     - TeraSky Laze Project B
tf_modules: []
```

> For an example of a complete YAML configuration file, look [here](examples/full-organization/organization.yaml)

## Requirements

Since this project is based on **CDK for Terraform**, you need to install it in order to deploy all resources.

Read [this](https://github.com/hashicorp/terraform-cdk/blob/main/docs/getting-started/python.md) for installation instructions (Python).

In addition, the following is required:

- An AWS account without (preferred) an organization (although LAZE can utilize the current organization if present)
- An IAM user with the `AdministratorAccess` policy attached
- Create access key for the above IAM user
- Create an AWS CLI profile (on the machine running Terraform) with the `access_key` and `secret_access_key` of the above user

## Development

For reference on Terraform CDK and the AWS provider, look here:

- [CDK for Terraform](https://github.com/hashicorp/terraform-cdk)
- [Terraform CDK aws Provider](https://github.com/hashicorp/cdktf-provider-aws/tree/main/src)

## Deployment

Install Python requirements:

```bash
pip install -r terraform-cdk/requirements.txt
```

Set an environment variable with the path to the YAML configuration file that describes the environment:

```bash
export CONFIG_FILE_PATH="/path/to/yaml"
```

Change to the `terraform-cdk` folder and get all dependencies:

```bash
cd terraform-cdk/
```

Once done, you can deploy the stack:

```bash
cdktf deploy
```

To destroy the stack (environment), run the following command inside the `terraform-cdk` folder:

```bash
cdktf destroy
```

## Example

The example below will create a new organization with a few accounts and resources. To deploy the example, run the following:

```bash
cd terraform-cdk/
pip install -r requirements.txt
export CONFIG_FILE_PATH="../examples/full-organization/organization.yaml"
cdktf deploy
```

## Limitations

- All resource names (SCPs, OUs, accounts) must be unique in the organization
- Account emails must be unique across all AWS
- The `Log Archive` and `Audit` accounts are currently dependent on each, so you can't choose to deploy just 1 of them (either none, or both)
