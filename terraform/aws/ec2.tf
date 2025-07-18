# Traffic to the ECS cluster should only come from the ALB
resource "aws_security_group" "sg_alb" {
  name        = "ccm-${var.tenant}-securitygroup-alb-to-ecs"
  description = "ALB to ECS internal traffic"
  vpc_id      = var.aws_vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}