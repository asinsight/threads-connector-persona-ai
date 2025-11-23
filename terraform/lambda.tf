locals {
  lambda_function_name = "threads-persona-writer"
}

module "threads_persona_lambda" {
  source        = "./modules/lambda_function"
  function_name = local.lambda_function_name
  role_arn      = module.lambda_role.role_arn
  image_uri     = var.lambda_image_uri
  timeout       = 60
  tags          = var.tags

  environment = {
    PERSONA_BUCKET                  = module.persona_bucket.bucket_name
    PERSONA_KEYS                    = join(",", var.persona_files)
    OPENAI_SECRET_NAME              = var.openai_secret_name
    THREADS_API_SECRET_NAME         = var.threads_api_secret_name
    THREADS_CONNECTOR_FUNCTION_NAME = var.threads_connector_function_name
    THREADS_USER_ID                 = var.threads_user_id
  }
}
