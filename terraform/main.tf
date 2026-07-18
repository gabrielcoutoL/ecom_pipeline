provider "aws" {
  region = "us-east-1"
}

terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket       = "gclauar-terraform-state"
    key          = "ecom_pipeline/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

# ------------------------------------------------------------------
# BUCKETS
# ------------------------------------------------------------------

resource "aws_s3_bucket" "ecom_bronze" {
  bucket = "lake-ecom-bronze-gclauar"
  tags   = { Ambiente = "Ecom-pipeline", Camada = "Bronze" }
}

resource "aws_s3_bucket" "ecom_silver" {
  bucket = "lake-ecom-silver-gclauar"
  tags   = { Ambiente = "Ecom-pipeline", Camada = "Silver" }
}

resource "aws_s3_bucket" "ecom_gold" {
  bucket = "lake-ecom-gold-gclauar"
  tags   = { Ambiente = "Ecom-pipeline", Camada = "Gold" }
}

locals {
  buckets = {
    bronze = aws_s3_bucket.ecom_bronze.id
    silver = aws_s3_bucket.ecom_silver.id
    gold   = aws_s3_bucket.ecom_gold.id
  }
}

resource "aws_s3_bucket_public_access_block" "lake" {
  for_each                = local.buckets
  bucket                  = each.value
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lake" {
  for_each = local.buckets
  bucket   = each.value
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake" {
  for_each = local.buckets
  bucket   = each.value
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# ------------------------------------------------------------------
# IAM — ROLE DA LAMBDA (ingestão -> bronze)
# ------------------------------------------------------------------

resource "aws_iam_role" "lambda_ecom_role" {
  name = "role-lambda-ecom-pipeline-gclauar"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_ecom_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "lambda-bronze-access"
  role = aws_iam_role.lambda_ecom_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject"]
        Resource = "${aws_s3_bucket.ecom_bronze.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.ecom_bronze.arn
      }
    ]
  })
}

# ------------------------------------------------------------------
# GLUE CATALOG
# ------------------------------------------------------------------

resource "aws_glue_catalog_database" "ecom_db_bronze" {
  name        = "db_ecom_bronze"
  description = "Database para as tabelas Bronze do Lake de Ecommerce"
}

resource "aws_glue_catalog_database" "ecom_db_silver" {
  name        = "db_ecom_silver"
  description = "Database para as tabelas Silver do Lake de Ecommerce"
}

resource "aws_glue_catalog_database" "ecom_db_gold" {
  name        = "db_ecom_gold"
  description = "Database para as tabelas Gold do Lake de Ecommerce"
}