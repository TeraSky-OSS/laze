resource "aws_iam_role" "admin_exec_role" {
  name = "${var.managed_resource_prefix}-AdministratorExecutionRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          AWS = "arn:aws:iam::${var.audit_account_id}:role/${var.managed_resource_prefix}-AuditAdministratorRole"
        }
      },
    ]
  })

  managed_policy_arns = [data.aws_iam_policy.administrator_access.arn]
}

resource "aws_iam_role" "read_only_exec_role" {
  name = "${var.managed_resource_prefix}-ReadOnlyExecutionRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          AWS = "arn:aws:iam::${var.audit_account_id}:role/${var.managed_resource_prefix}-AuditReadOnlyRole"
        }
      },
    ]
  })

  managed_policy_arns = [data.aws_iam_policy.read_only_access.arn]
}