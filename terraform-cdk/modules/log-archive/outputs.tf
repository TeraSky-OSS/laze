output "logging_bucket_name" {
  description = "S3 Access Logging Bucket name"
  value       = aws_s3_bucket.logging.bucket
}

output "audit_bucket_name" {
  description = "Audit S3 bucket name"
  value       = aws_s3_bucket.audit.bucket
}

output "config_recorder_role_arn" {
  description = "Config Role ARN"
  value       = aws_iam_role.config_recorder.arn
}

output "local_security_topic_arn" {
  description = "Local Security Notification SNS Topic ARN"
  value       = aws_sns_topic.local_security.arn
}

output "local_security_topic_name" {
  description = "Local Security Notification SNS Topic Name"
  value       = aws_sns_topic.local_security.name
}