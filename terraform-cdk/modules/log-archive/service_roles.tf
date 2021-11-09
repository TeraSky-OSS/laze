resource "aws_iam_role" "config_recorder" {
  name = "${var.managed_resource_prefix}-ConfigRecorderRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    data.aws_iam_policy.aws_config_rule.arn,
    data.aws_iam_policy.read_only_access.arn
  ]
}

resource "aws_iam_role" "forward_sns_notification_lambda" {
  name = "${var.managed_resource_prefix}-ForwardSnsNotificationRole"
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    data.aws_iam_policy.aws_lambda_exec_role.arn
  ]

  inline_policy {
    name   = "sns"
    policy = data.aws_iam_policy_document.sns_inline_policy.json
  }
}

data "aws_iam_policy_document" "sns_inline_policy" {
  statement {
    effect = "Allow"
    actions   = ["sns:publish"]
    resources = ["arn:aws:sns:*:${var.audit_account_id}:${var.managed_resource_prefix}-AggregateSecurityNotifications"]
  }
}