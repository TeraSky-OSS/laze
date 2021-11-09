### Logging Bucket ###
resource "aws_s3_bucket" "logging" {
  bucket        = "${var.managed_resource_prefix}-s3-access-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  acl           = "log-delivery-write"
  force_destroy = true

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        # kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logging" {
  bucket = aws_s3_bucket.logging.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "logging" {
  bucket = aws_s3_bucket.logging.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowSSLRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.logging.arn,
          "${aws_s3_bucket.logging.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
    ]
  })

  # Workaround since "aws_s3_bucket_public_access_block" and "aws_s3_bucket_policy" resources
  # can't be created at the same time
  depends_on = [
    aws_s3_bucket_public_access_block.logging
  ]
}

### Audit Bucket ###
resource "aws_s3_bucket" "audit" {
  bucket        = "${var.managed_resource_prefix}-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  force_destroy = true

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.logging.id
    # target_prefix = "log/"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        # kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "RetentionRule"
    enabled = true

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket = aws_s3_bucket.audit.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "audit" {
  bucket = aws_s3_bucket.audit.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowSSLRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.audit.arn,
          "${aws_s3_bucket.audit.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid    = "AWSBucketPermissionsCheck"
        Effect = "Allow"
        Principal = {
          Service = [
            "cloudtrail.amazonaws.com",
            "config.amazonaws.com"
          ]
        }
        Action   = "s3:GetBucketAcl"
        Resource = [aws_s3_bucket.audit.arn]
      },
      {
        Sid    = "AWSConfigBucketExistenceCheck"
        Effect = "Allow"
        Principal = {
          Service = [
            "cloudtrail.amazonaws.com",
            "config.amazonaws.com"
          ]
        }
        Action   = "s3:ListBucket"
        Resource = [aws_s3_bucket.audit.arn]
      },
      {
        Sid    = "AWSBucketDelivery"
        Effect = "Allow"
        Principal = {
          Service = [
            "cloudtrail.amazonaws.com",
            "config.amazonaws.com"
          ]
        }
        Action   = "s3:PutObject"
        Resource = ["${aws_s3_bucket.audit.arn}/${data.aws_organizations_organization.current.id}/AWSLogs/*/*"]
      },
    ]
  })

  # Workaround since "aws_s3_bucket_public_access_block" and "aws_s3_bucket_policy" resources
  # can't be created at the same time
  depends_on = [
    aws_s3_bucket_public_access_block.audit
  ]
}
