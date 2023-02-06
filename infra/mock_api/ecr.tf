resource "aws_ecr_repository" "mock-api-repository" {
  name                 = "mock-api-repo"
  image_tag_mutability = "MUTABLE"
}