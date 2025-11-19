output "persona_bucket_name" {
  description = "S3 bucket that holds persona guideline files"
  value       = module.persona_bucket.bucket_name
}

output "lambda_function_arn" {
  description = "ARN of the Threads persona Lambda function"
  value       = module.threads_persona_lambda.function_arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule that triggers the Lambda"
  value       = module.threads_schedule.rule_arn
}
