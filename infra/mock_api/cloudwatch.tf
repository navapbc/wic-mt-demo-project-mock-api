# ----------------------------------------------
# Mock API
# ----------------------------------------------
resource "aws_cloudwatch_log_group" "mock_api" {
  name              = "mock-api"
  retention_in_days = 90
}
