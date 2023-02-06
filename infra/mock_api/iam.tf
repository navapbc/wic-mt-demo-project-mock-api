# add ecr perms (push)
data "aws_iam_policy_document" "deploy_action" {
  statement {
    sid     = "WICUpdateECR"
    actions = ["ecs:UpdateCluster", "ecs:UpdateService", "ecs:DescribeClusters", "ecs:DescribeServices", "ecr:*"]
    resources = [
      "arn:aws:ecs:us-east-1:546642427916:service/${var.environment_name}/*",
      "arn:aws:ecs:us-east-1:546642427916:cluster/${var.environment_name}",
      aws_ecr_repository.mock-api-repository.arn
    ]
  }
  statement {
    sid       = "WICLogin"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
}