#!/bin/sh

send_slack_alert() {
  if [ -n "$ALERT_SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"$1\"}" \
      "$ALERT_SLACK_WEBHOOK"
  fi
}

dbt --no-use-colors build
error_code=$?
if [ "$error_code" -ne 0 ] ; then
  send_slack_alert ":x: - $_TENANT - Data pipeline job failed with error code $error_code"
  exit $error_code
else
  send_slack_alert ":white_check_mark: - $_TENANT - Data pipeline job completed successfully"
  exit 0
fi
