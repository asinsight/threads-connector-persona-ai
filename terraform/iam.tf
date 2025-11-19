locals {
  lambda_role_name = "threads-persona-lambda-role"
}

module "lambda_role" {
  source             = "./modules/iam_lambda_role"
  role_name          = local.lambda_role_name
  persona_bucket_arn = module.persona_bucket.bucket_arn
  tags               = var.tags
}
