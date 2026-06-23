output "site_bucket_name" {
  description = "S3 bucket used for the built static site files."
  value       = aws_s3_bucket.site.bucket
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID. Use this for cache invalidations."
  value       = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "site_url" {
  description = "Primary URL for the site."
  value       = local.use_custom_domain ? "https://${var.domain_name}" : "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "deploy_command" {
  description = "Example command to upload Astro's dist directory and invalidate CloudFront."
  value       = "aws s3 sync ../../dist s3://${aws_s3_bucket.site.bucket}/ --delete && aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.site.id} --paths '/*'"
}
