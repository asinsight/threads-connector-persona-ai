locals {
  ecr_repository_name = "threads-persona-writer"
}

module "lambda_ecr_repository" {
  source          = "./modules/ecr_repository"
  repository_name = local.ecr_repository_name
  tags            = var.tags
}
