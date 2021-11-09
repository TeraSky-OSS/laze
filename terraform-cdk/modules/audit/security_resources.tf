resource "aws_iam_role" "administration_role" {
  name = "${var.managed_resource_prefix}-AuditAdministratorRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    data.aws_iam_policy.lambda_exec.arn
  ]

  inline_policy {
    name   = "AssumeRole-${var.managed_resource_prefix}-AuditAdministratorRole"
    policy = data.aws_iam_policy_document.admin_inline_policy.json
  }
}

data "aws_iam_policy_document" "admin_inline_policy" {
  statement {
    effect = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = ["arn:aws:iam::*:role/${var.managed_resource_prefix}-AdministratorExecutionRole"]
  }
}

resource "aws_iam_role" "read_only_role" {
  name = "${var.managed_resource_prefix}-AuditReadOnlyRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    data.aws_iam_policy.lambda_exec.arn
  ]

  inline_policy {
    name   = "AssumeRole-${var.managed_resource_prefix}-AuditReadOnlyRole"
    policy = data.aws_iam_policy_document.read_only_inline_policy.json
  }
}

data "aws_iam_policy_document" "read_only_inline_policy" {
  statement {
    effect = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = ["arn:aws:iam::*:role/${var.managed_resource_prefix}-ReadOnlyExecutionRole"]
  }
}

# AWSConfig Aggregator for Guardrail compliance
resource "aws_config_configuration_aggregator" "guardrails_compliance" {
  name = "${var.managed_resource_prefix}-GuardrailsComplianceAggregator"

  account_aggregation_source {
    account_ids = distinct([data.aws_caller_identity.current.account_id, var.log_archive_account_id])
    all_regions = true
  }
}