{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric", "crowdstrike"]
    )
}}

WITH unremediated_vulns AS (
    SELECT 
        v.asset_uuid,
        COUNT(*) AS vuln_count
    FROM {{ source('source','tenable_vulnerabilities') }} v
    WHERE 
        v.plugin_cpe like '%cpe:/a:%' AND
        v.has_patch AND
        {{ days_to_today('v.plugin_published_date', 'CURRENT_DATE') }} > 0 AND
        v.state IN ('OPEN', 'REOPENED')
    GROUP BY v.asset_uuid
)

SELECT 
    'VM02' AS metric_id,
    ta.hostnames AS resource,
    ta.upload_timestamp,
    
    CASE 
        WHEN uv.vuln_count IS NULL THEN 1
        ELSE 0
    END AS compliance,

    CASE 
        WHEN uv.vuln_count IS NULL THEN 'No critical updates found'
        ELSE 'Patch or upgrade your applications to remediate ' || uv.vuln_count || ' vulnerabilities.'
    END AS detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','tenable_assets') }} ta
LEFT JOIN unremediated_vulns uv 
    ON uv.asset_uuid = ta.id
WHERE
    {{ days_to_today('ta.last_seen','ta.upload_timestamp') }} < 7
