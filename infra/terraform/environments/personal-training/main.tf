module "static_site" {
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
  source = "../../modules/static-site"

  project_name     = "deals-madmallardpersonaltraining-com"
  environment      = "prod"
  aws_region       = var.aws_region
  domain_name      = var.domain_name
  hosted_zone_name = var.hosted_zone_name
  create_dns_record = var.create_dns_record
  price_class      = var.price_class
  enable_ipv6      = true
}
