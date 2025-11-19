variable "rule_name" {
  description = "Name of the EventBridge rule"
  type        = string
}

variable "schedule_expression" {
  description = "Schedule expression for the EventBridge rule"
  type        = string
}

variable "lambda_arn" {
  description = "ARN of the Lambda function to invoke"
  type        = string
}

variable "lambda_name" {
  description = "Name of the Lambda function to invoke"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the EventBridge rule"
  type        = map(string)
  default     = {}
}

resource "aws_cloudwatch_event_rule" "this" {
  name                = var.rule_name
  schedule_expression = var.schedule_expression
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "this" {
  rule      = aws_cloudwatch_event_rule.this.name
  target_id = "${var.rule_name}-target"
  arn       = var.lambda_arn
}

resource "aws_lambda_permission" "this" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.this.arn
}

output "rule_arn" {
  value       = aws_cloudwatch_event_rule.this.arn
  description = "EventBridge rule ARN"
}
