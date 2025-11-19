locals {
  eventbridge_rule_name = "threads-persona-every-5-hours"
}

module "threads_schedule" {
  source               = "./modules/eventbridge_schedule"
  rule_name            = local.eventbridge_rule_name
  schedule_expression  = "rate(5 hours)"
  lambda_arn           = module.threads_persona_lambda.function_arn
  lambda_name          = module.threads_persona_lambda.function_name
  tags                 = var.tags
}
