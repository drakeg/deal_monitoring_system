variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "domain_name" {
  type    = string
  default = "deals.madmallardpersonaltraining.com"
}

variable "hosted_zone_name" {
  type        = string
  description = "Route 53 hosted zone name. Leave empty to skip DNS creation."
  default     = ""
}

variable "price_class" {
  type    = string
  default = "PriceClass_100"
}

variable "create_dns_record" {
  type        = bool
  description = "Create Route 53 DNS records for this site. Requires hosted_zone_name."
  default     = false
}
