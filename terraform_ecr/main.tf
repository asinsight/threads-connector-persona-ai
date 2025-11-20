terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.profile_name
}

locals {
  ecr_repository_name = "threads-persona-writer"
}

module "lambda_ecr_repository" {
  source          = "./modules/ecr_repository"
  repository_name = local.ecr_repository_name
  tags            = var.tags
}
