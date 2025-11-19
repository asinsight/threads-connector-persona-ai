variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
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
  description = "ECR image URI for the Lambda function"
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

variable "threads_post_url" {
  description = "API Gateway URL for posting Threads content"
  type        = string
  default     = "https://aylhkweg4d.execute-api.us-east-1.amazonaws.com/dev/post"
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
