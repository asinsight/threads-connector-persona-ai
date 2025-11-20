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

variable "tags" {
  description = "Tags applied to created resources"
  type        = map(string)
  default     = {}
}
