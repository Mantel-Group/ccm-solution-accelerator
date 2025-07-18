{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","tenable"]
    )
}}

SELECT 
    'OP01' AS metric_id,
    ta.hostnames AS resource,
    ta.upload_timestamp,
    
    CASE 
        WHEN {{ days_to_today('ta.last_seen','ta.upload_timestamp') }} < 31 THEN 1
        ELSE 0
    END AS compliance,

    CASE 
        WHEN {{ days_to_today('ta.last_seen','ta.upload_timestamp') }} < 31 THEN 'Tenable Host seen in the last 31 days - ' || ta.last_seen
        ELSE 'Tenable Host not seen in the last 31 days - ' || ta.last_seen
    END AS detail,  

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','tenable_assets') }} ta
WHERE
    ta.hostnames is not null
