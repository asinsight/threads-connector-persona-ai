output "ecr_repository_url" {
  description = "ECR repository URL for the Lambda Docker image"
  value       = module.lambda_ecr_repository.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name"
  value       = module.lambda_ecr_repository.repository_name
}

output "ecr_repository_arn" {
  description = "ECR repository ARN"
  value       = module.lambda_ecr_repository.repository_arn
}
