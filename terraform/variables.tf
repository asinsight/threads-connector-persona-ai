variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "profile_name" {
  description = "AWS CLI profile name"
  type        = string
  default     = "swiri021"
}

variable "persona_bucket_name" {
  description = "S3 bucket name that stores persona guideline files"
  type        = string
}

variable "persona_files" {
  description = "List of persona files to load from the S3 bucket"
  type        = list(string)
  default     = ["chief.txt", "stock_analyzer.txt"]
}

variable "lambda_image_uri" {
  description = "ECR image URI for the Lambda function (format: account.dkr.ecr.region.amazonaws.com/repo:tag)"
  type        = string
}

variable "openai_secret_name" {
  description = "AWS Secrets Manager secret name containing OpenAI credentials"
  type        = string
}

variable "threads_api_secret_name" {
  description = "AWS Secrets Manager secret name containing API Gateway API key"
  type        = string
}

variable "threads_connector_function_name" {
  description = "Name of the Threads Connector Lambda function to invoke"
  type        = string
  default     = "threads-connector-dev-api"
}

variable "threads_user_id" {
  description = "User identifier passed to the Threads API"
  type        = string
  default     = "default"
}

variable "tags" {
  description = "Tags applied to created resources"
  type        = map(string)
  default     = {}
}
