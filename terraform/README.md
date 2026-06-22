# Terraform: AWS Static Site Hosting

This Terraform deploys the Mad Mallard Deals static site using a low-cost AWS architecture:

- Private S3 bucket for built files
- CloudFront CDN in front of S3
- CloudFront Origin Access Control, so the bucket is not public
- Optional ACM certificate for a custom domain
- Optional Route 53 DNS records

No EC2, ECS, RDS, or always-on application server is required.

## Prerequisites

- AWS CLI configured with credentials
- Terraform >= 1.6
- Node.js >= 20
- An AWS account with permissions for S3, CloudFront, ACM, IAM policy attachment, and optionally Route 53

## First-time setup

From the repo root:

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

Edit `infra/terraform/terraform.tfvars`.

For the cheapest first deployment, leave `domain_name` blank and use the generated CloudFront URL.

```hcl
domain_name       = ""
create_dns_record = false
```

If using a custom domain in Route 53:

```hcl
domain_name       = "deals.example.com"
hosted_zone_name  = "example.com"
create_dns_record = true
```

## Deploy infrastructure

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Build and upload the site

From the repo root:

```bash
npm install
npm run build
cd infra/terraform
aws s3 sync ../../dist s3://$(terraform output -raw site_bucket_name)/ --delete
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths '/*'
```

Then open:

```bash
terraform output -raw site_url
```

## Destroy

This will remove the hosting infrastructure. Empty the S3 bucket first if Terraform cannot delete it.

```bash
cd infra/terraform
aws s3 rm s3://$(terraform output -raw site_bucket_name)/ --recursive
terraform destroy
```

## Cost notes

This is designed to stay very low cost for a small static affiliate site. Costs can still occur for CloudFront traffic, S3 storage/requests, Route 53 hosted zones, and domain registration.
