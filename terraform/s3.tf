module "persona_bucket" {
  source      = "./modules/s3_bucket"
  bucket_name = var.persona_bucket_name
  tags        = var.tags
}
