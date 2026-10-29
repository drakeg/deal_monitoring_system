terraform {
  required_version = ">= 1.17.1"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 6.71"
      configuration_aliases = [aws.us_east_1]
    }
  }
}
