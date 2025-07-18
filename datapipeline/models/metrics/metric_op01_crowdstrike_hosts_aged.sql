{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","crowdstrike"]
    )
}}

SELECT 
    'OP01' AS metric_id,
    cs.serial_number AS resource,
    cs.upload_timestamp,
    
    CASE
        WHEN {{ days_to_today('cs.last_seen','cs.upload_timestamp') }} < 31 THEN 1
        ELSE 0
    END AS compliance,

    CASE 
        WHEN {{ days_to_today('cs.last_seen','cs.upload_timestamp') }} < 31 THEN 'Crowdstrike Host seen in the last 31 days - ' || cs.last_seen
        ELSE 'Crowdstrike Host not seen in the last 31 days - ' || cs.last_seen
    END AS detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','crowdstrike_hosts') }} cs
WHERE
    cs.serial_number is not null
