variable "email_from" {
  type = string
}
variable "email_to" {
  type = string
}

resource "aws_lambda_function" "mrb_scraper" {
  function_name = "mrb_scraper"
  filename      = "${path.module}/data/placeholder_lambda.zip"
  role          = aws_iam_role.lambda_mrb_scraper.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"
  timeout       = 600

  environment {
    variables = {
      EMAIL_FROM = var.email_from
      EMAIL_TO   = var.email_to
    }
  }
}

resource "aws_cloudwatch_event_rule" "mrb_scraper" {
  schedule_expression = "rate(6 hours)"
}

resource "aws_cloudwatch_event_target" "mrb_scraper" {
  rule = aws_cloudwatch_event_rule.mrb_scraper.name
  arn  = aws_lambda_function.mrb_scraper.arn
}

resource "aws_lambda_permission" "mrb_scraper" {
  statement_id  = "AllowExecutionFromCloudwatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mrb_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.mrb_scraper.arn
}
