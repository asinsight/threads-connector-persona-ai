variable "role_name" {
  description = "Name of the IAM role"
  type        = string
}

variable "persona_bucket_arn" {
  description = "ARN of the persona S3 bucket"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the IAM role"
  type        = map(string)
  default     = {}
}

resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}

resource "aws_iam_role_policy" "this" {
  name   = "${var.role_name}-policy"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions   = ["s3:GetObject"]
    resources = ["${var.persona_bucket_arn}/*"]
  }

  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = ["*"]
  }
}

output "role_arn" {
  value       = aws_iam_role.this.arn
  description = "IAM role ARN"
}

output "role_name" {
  value       = aws_iam_role.this.name
  description = "IAM role name"
}
