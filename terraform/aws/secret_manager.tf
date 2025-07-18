# resource "aws_secretsmanager_secret" "db_master_password" {
#   name = "continuous-assurance-db-master-${var.tenant}"
# }

# resource "aws_secretsmanager_secret_version" "db-pass-val" {
#     secret_id = aws_secretsmanager_secret.db_master_password.id

# }