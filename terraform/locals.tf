locals {
  use_custom_domain = trimspace(var.domain_name) != ""
  create_dns        = local.use_custom_domain && var.create_dns_record

  # S3 bucket names must be globally unique. If this name is already taken,
  # override project_name or use a custom terraform.tfvars value.
  site_bucket_name = lower(replace("${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}", "_", "-"))

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}
