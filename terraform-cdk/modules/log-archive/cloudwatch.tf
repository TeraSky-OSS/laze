locals {
  security_topic_name = "${var.managed_resource_prefix}-AggregateSecurityNotifications"
}

module "lambda_forward_sns_notification" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "2.18.0"

  function_name = "${var.managed_resource_prefix}-NotificationForwarder"
  description   = "SNS message forwarding function for aggregating account notifications"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"
  memory_size   = 128
  timeout       = 60

  environment_variables = {
    sns_arn = "arn:aws:sns:${data.aws_region.current.name}:${var.audit_account_id}:${local.security_topic_name}"
  }

  source_path = "${path.module}/files/index.py"

  tags = {
    Name = "my-lambda1"
  }
}

resource "aws_sns_topic" "local_security" {
  name         = "${var.managed_resource_prefix}-SecurityNotifications"
  display_name = "${var.managed_resource_prefix}-SecurityNotifications"
}

resource "aws_sns_topic_policy" "local_security" {
  arn = aws_sns_topic.local_security.arn

  policy = data.aws_iam_policy_document.local_security.json
}

data "aws_iam_policy_document" "local_security" {
  statement {
    sid = "__default_statement_ID"

    effect = "Allow"
  
    actions = [
      "SNS:Subscribe",
      "SNS:SetTopicAttributes",
      "SNS:RemovePermission",
      "SNS:Receive",
      "SNS:Publish",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:DeleteTopic",
      "SNS:AddPermission",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceOwner"
      values   = [data.aws_caller_identity.current.account_id]
    }

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      aws_sns_topic.local_security.arn,
    ]
  }

  statement {
    sid = "TrustCWEToPublishEventsToMyTopic"

    effect = "Allow"
  
    actions = [
      "sns:Publish",
    ]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [
      aws_sns_topic.local_security.arn,
    ]
  }
}

resource "aws_sns_topic_subscription" "local_security" {
  topic_arn = aws_sns_topic.local_security.arn
  protocol  = "lambda"
  endpoint  = module.lambda_forward_sns_notification.lambda_function_arn
}

resource "aws_lambda_permission" "local_security" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_forward_sns_notification.lambda_function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.local_security.arn
}

# Enable notifications for AWS Config Rule compliance changes
resource "aws_cloudwatch_event_rule" "compliance_change_event" {
  name        = "${var.managed_resource_prefix}-ConfigComplianceChangeEventRule"
  description = "CloudWatch Event Rule to send notification on Config Rule compliance changes"

  event_pattern = <<EOF
{
  "source": [
    "aws.config"
  ],
  "detail-type": [
    "Config Rules Compliance Change"
  ]
}
EOF
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.compliance_change_event.name
  target_id = "Compliance-Change-Topic"
  arn       = aws_sns_topic.local_security.arn
}