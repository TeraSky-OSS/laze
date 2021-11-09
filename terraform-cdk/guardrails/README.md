# Guardrails

The policies in this folder were collected from Control Tower console.

To collect the policies (manually, as there is no API):

- Browse to Control Tower console
- Move to Guardrails tag
- Sort the Guardrails by Behavior
- Choose the `Prevention` for SCPs or `Detection` for Config rules

## Service Control Policies (SCPs)

| Name | Description | File |
|------|-------------|------|
| Disallow deletion of log archive | Prevent deletion of Amazon S3 buckets created by AWS Control Tower in the log archive account | audit_bucket_deletion_prohibited |
| Disallow Changes to Encryption Configuration for Amazon S3 Buckets | Prevent changes to encryption configuration for your Amazon S3 buckets | audit_bucket_encryption_enabled |
| Disallow Changes to Logging Configuration for Amazon S3 Buckets | Prevent changes to bucket logging for your Amazon S3 buckets | audit_bucket_logging_enabled |
| Disallow Changes to Bucket Policy for Amazon S3 Buckets | Prevent changes to bucket policy for your Amazon S3 buckets | audit_bucket_policy_changes_prohibited |
| Disallow Changes to Lifecycle Configuration for Amazon S3 Buckets | Prevent changes to lifecycle configuration for your Amazon S3 buckets | audit_bucket_retention_policy |
| Disallow configuration changes to CloudTrail | Log API activity in a consistent manner by ensuring that your AWS CloudTrail settings do not change | cloudtrail_change_prohibited |
| Integrate CloudTrail events with CloudWatch Logs | Perform real-time analysis of activity data by sending AWS CloudTrail events to AWS CloudWatch logs | cloudtrail_cloudwatch_logs_enabled |
| Enable CloudTrail in all available regions | Track AWS API call activity within your accounts using AWS CloudTrail, which records call history including the identity of the caller and the time of the call | cloudtrail_enabled |
| Enable integrity validation for CloudTrail log file | Protect the integrity of account activity logs using AWS CloudTrail log file validation, which creates a digitally signed digest file that contains a hash of each log that CloudTrail writes to Amazon S3 | cloudtrail_validation_enabled |
| Disallow changes to Amazon CloudWatch set up by AWS Control Tower | Prevent changes to Amazon CloudWatch configuration set up by AWS Control Tower to monitor your environment | cloudwatch_events_change_prohibited |
| Disallow deletion of AWS Config Aggregation Authorizations created by AWS Control Tower | Prevent deletion of AWS Config aggregation authorizations created by AWS Control Tower | config_aggregation_authorization_policy |
| Disallow changes to tags created by AWS Control Tower for AWS Config resources | Prevents updates or deletion of tags created by AWS Control Tower for AWS Config resources | config_aggregation_change_prohibited |
| Disallow configuration changes to AWS Config | Record resource configurations in a consistent manner by ensuring that AWS Config settings don't change | config_change_prohibited |
| Enable AWS Config in all available regions | Identify configuration changes to AWS resources using AWS Config | config_enabled |
| Disallow changes to AWS Config Rules set up by AWS Control Tower | Prevent changes to AWS Config Rules set up by AWS Control Tower | config_rule_change_prohibited |
| Disallow Changes to Encryption Configuration for AWS Control Tower Created S3 Buckets in Log Archive | Prevent encryption configuration changes to Amazon S3 buckets created by AWS Control Tower | ct_audit_bucket_encryption_changes_prohibited |
| Disallow changes to lifecycle configuration for AWS Control Tower created Amazon S3 buckets in log archive | Prevent lifecycle configuration changes to Amazon S3 buckets created by AWS Control Tower | ct_audit_bucket_lifecycle_configuration_changes_prohibited |
| Disallow changes to logging configuration for AWS Control Tower created Amazon S3 buckets in log archive | Prevent logging configuration changes to the Amazon S3 buckets created by AWS Control Tower | ct_audit_bucket_logging_configuration_changes_prohibited |
| Disallow changes to bucket policy for AWS Control Tower created Amazon S3 buckets in log archive | Prevent bucket policy changes to the Amazon S3 buckets created by AWS Control Tower | ct_audit_bucket_policy_changes_prohibited |
| Disallow changes to AWS IAM roles set up by AWS Control Tower and AWS CloudFormation | Prevent changes to AWS IAM roles set up for your accounts by AWS Control Tower and AWS CloudFormation | iam_role_change_prohibited |
| Disallow changes to AWS Lambda functions set up by AWS Control Tower | Prevent changes to AWS Lambda functions set up by AWS Control Tower | lambda_change_prohibited |
| Disallow changes to Amazon CloudWatch Logs log groups set up by AWS Control Tower | Prevent deletion and modification of retention policy for Amazon CloudWatch Logs log groups set up by AWS Control Tower | log_group_policy |
| Disallow actions as a root user | Secure your AWS accounts by disallowing account access with root user credentials, which are credentials of the account owner and allow unrestricted access to all resources in the account. We recommend that you instead create AWS Identity and Access Management (IAM) users for everyday interaction with your AWS account | restrict_root_user |
| Disallow creation of access keys for the root user | Secure your AWS accounts by disallowing creation of access keys for the root user, which will allow unrestricted access to all resources in the account. We recommend that you instead create access keys for an AWS Identity and Access Management (IAM) user for everyday interaction with your AWS account | restrict_root_user_access_keys |
| Disallow changes to replication configuration for Amazon S3 buckets | Prevent changes to replication configuration for Amazon S3 buckets | restrict_s3_cross_region_replication |
| Disallow delete actions on S3 buckets without MFA | Protect your Amazon S3 buckets by requiring multi-factor authentication (MFA) for delete actions. MFA requires an additional authentication code after the user name and password are successful | restrict_s3_delete_without_mfa |
| Disallow changes to Amazon SNS set up by AWS Control Tower | Prevent changes to Amazon SNS notification settings set up by AWS Control Tower | sns_change_prohibited |
| Disallow changes to Amazon SNS subscriptions set up by AWS Control Tower | Prevent changes to Amazon SNS subscriptions set up by AWS Control Tower to trigger notifications for AWS Config Rule compliance changes | sns_subscription_change_prohibited |
