variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "mad-mallard-deals"
}

variable "aws_region" {
  description = "Primary AWS region for S3 and Route 53 resources. CloudFront is global."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "prod"
}

variable "domain_name" {
  description = "Optional custom domain, for example deals.madmallards.com. Leave blank to use the CloudFront domain only."
  type        = string
  default     = ""
}

variable "hosted_zone_name" {
  description = "Optional Route 53 hosted zone name, for example madmallards.com. Required if create_dns_record is true."
  type        = string
  default     = ""
}

variable "create_dns_record" {
  description = "Create a Route 53 A/AAAA alias record for domain_name. Requires hosted_zone_name and domain_name."
  type        = bool
  default     = false
}

variable "price_class" {
  description = "CloudFront price class. PriceClass_100 is the cheapest global edge footprint."
  type        = string
  default     = "PriceClass_100"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.price_class)
    error_message = "price_class must be PriceClass_100, PriceClass_200, or PriceClass_All."
  }
}

variable "enable_ipv6" {
  description = "Enable IPv6 for CloudFront."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to resources."
  type        = map(string)
  default     = {}
}
