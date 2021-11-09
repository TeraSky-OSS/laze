data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_organizations_organization" "current" {}

data "aws_iam_policy" "lambda_exec" {
  arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}
