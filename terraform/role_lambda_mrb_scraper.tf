data "aws_iam_policy_document" "lambda_mrb_scraper_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "lambda_mrb_scraper" {
  name               = "lambda_mrb_scraper"
  assume_role_policy = data.aws_iam_policy_document.lambda_mrb_scraper_assume.json
}

data "aws_iam_policy_document" "lambda_mrb_scraper_permissions" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "lambda:UpdateFunctionCode",
    ]
    resources = [aws_lambda_function.mrb_scraper.arn]
  }

  statement {
    actions   = ["ses:SendRawEmail"]
    resources = ["*"]
  }
}
resource "aws_iam_role_policy" "lambda_mrb_scraper_permissions" {
  role   = aws_iam_role.lambda_mrb_scraper.id
  policy = data.aws_iam_policy_document.lambda_mrb_scraper_permissions.json
}
