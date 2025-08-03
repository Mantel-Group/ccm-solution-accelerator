import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def find_ip(tenant: str) -> str:
    """
    Return the public IP of the newest running dashboard task
    (ccm-<tenant>-task-dashboard) in the ccm-<tenant>-service service.
    """
    cluster           = f"ccm-{tenant}-cluster"
    service           = f"ccm-{tenant}-service"
    target_container  = f"ccm-{tenant}-task-dashboard"

    ecs = boto3.client("ecs")
    ec2 = boto3.client("ec2")

    tasks_rsp = ecs.list_tasks(
        cluster=cluster,
        serviceName=service,
        desiredStatus="RUNNING"
    )
    task_arns = tasks_rsp.get("taskArns", [])
    if not task_arns:
        raise RuntimeError("No running tasks found")

    newest_time = None
    newest_eni  = None

    for arn in task_arns:
        task = ecs.describe_tasks(cluster=cluster, tasks=[arn])["tasks"][0]

        if target_container not in [c["name"] for c in task["containers"]]:
            continue

        if 'startedAt' in task:
            started_at = task["startedAt"]
            eni_id = next(
                (d["value"]
                for att in task["attachments"]
                if att["type"] == "ElasticNetworkInterface"
                for d in att["details"]
                if d["name"] == "networkInterfaceId"),
                None
            )
            if eni_id and (newest_time is None or started_at > newest_time):
                newest_time, newest_eni = started_at, eni_id

    if newest_eni is None:
        raise RuntimeError("ENI not found")

    eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[newest_eni])["NetworkInterfaces"][0]
    return eni.get("Association", {}).get("PublicIp", "")


def lambda_handler(event, context):
    """
    Called via Lambda Function URL:
    - tenant can be supplied as ?tenant=<value>
    - or fixed via the TENANT environment variable.
    Responds with HTTP 302 redirect to http://<public‑ip>/
    """
    tenant = os.environ.get("TENANT")

    if not tenant:
        return {"statusCode": 400, "body": "Missing tenant parameter"}

    try:
        public_ip = find_ip(tenant)
    except (ClientError, NoCredentialsError, RuntimeError) as exc:
        return {"statusCode": 500, "body": str(exc)}

    if not public_ip:
        return {"statusCode": 502, "body": "Dashboard IP not available"}

    return {
        "statusCode": 302,
        "headers": {"Location": f"http://{public_ip}:8080"},
        "body": ""
    }
