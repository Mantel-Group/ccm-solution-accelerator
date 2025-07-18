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
        v.agent_id,
        COUNT(*) AS vuln_count
    FROM {{ source('source','crowdstrike_vulnerabilities') }} v
    LEFT JOIN {{ source('source','crowdstrike_vulnerabilities_remediation') }} r
        ON r.id = v.id 
        AND (
            r.action LIKE 'Update Apple Mac OS%' OR
            r.action LIKE 'Install patch for Microsoft Windows%'
        )
    WHERE 
        v.has_patch AND
        {{ days_to_today('v.published_on', 'CURRENT_DATE') }} > 0 AND
        v.status IN ('open', 'reopen') AND
        r.id IS NULL
    GROUP BY v.agent_id
)

SELECT 
    'VM01' AS metric_id,
    cs.serial_number AS resource,
    cs.upload_timestamp,
    
    CASE 
        WHEN uv.vuln_count IS NULL THEN 1
        ELSE 0
    END AS compliance,

    CASE 
        WHEN uv.vuln_count IS NULL THEN 'No critical updates found'
        ELSE 'Patch or upgrade your OS to remediate ' || uv.vuln_count || ' vulnerabilities.'
    END AS detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','crowdstrike_hosts') }} cs
LEFT JOIN unremediated_vulns uv 
    ON uv.agent_id = cs.device_id
WHERE
    cs.serial_number is not null AND
    {{ days_to_today('cs.last_seen','cs.upload_timestamp') }} < 7
