{{
    config(
        materialized="incremental",
        partition_by={
            "field": "activity_date_time",
            "data_type": "timestamp",
            "granularity": "day",
        },
        tags=["intermediate"]
    )
}}

{# Azure Audit Logs only retain 30 days of logs, so we need to build an incremental model to store the history #}

select
    *
from
    {{ source("source","azure_audit_logs") }}
{% if is_incremental() %}
    WHERE activity_date_time > (SELECT MAX(activity_date_time) FROM {{ this }})
{% endif %}
