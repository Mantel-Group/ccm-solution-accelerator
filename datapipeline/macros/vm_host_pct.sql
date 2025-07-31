{% macro vm_host_pct() %}

WITH crowdstrike_unremediated_vulns AS (
    SELECT 
        v.agent_id,
        COUNT(*) AS vuln_count
    FROM {{ source('source','crowdstrike_vulnerabilities') }} v
    LEFT JOIN {{ source('source','crowdstrike_vulnerabilities_remediation') }} r
        ON r.id = v.id

        {% if kwargs.is_operating_system == true %}
        AND (
            r.action LIKE 'Update Apple Mac OS%' OR
            r.action LIKE 'Install patch for Microsoft Windows%'
        )
        {% endif %}
        {% if kwargs.is_operating_system == false %}
        AND NOT (
            r.action LIKE 'Update Apple Mac OS%' OR
            r.action LIKE 'Install patch for Microsoft Windows%'
        )
        {% endif %}

    WHERE 
        v.status IN ('open', 'reopen')

        {% if kwargs.has_patch == true %}
            AND v.has_patch IS TRUE
        {% endif %}
        {% if kwargs.has_patch == false %}
            AND v.has_patch IS FALSE
        {% endif %}

        {% if kwargs.has_exploit == true %}
            AND v.has_exploit IS TRUE
        {% endif %}
        {% if kwargs.has_exploit == false %}
            AND v.has_patch IS FALSE
        {% endif %}

        {% if kwargs.published %}
        AND {{ days_to_today('v.published_on', 'CURRENT_DATE') }} > {{ kwargs.published }}
        {% endif %}

        AND r.id IS NULL
    GROUP BY v.agent_id
), unremediated_vulns_tenable AS (
    SELECT 
        v.asset_uuid,
        COUNT(*) AS vuln_count
    FROM {{ source('source','tenable_vulnerabilities') }} v
    WHERE 
        v.state IN ('OPEN', 'REOPENED')

        {% if kwargs.is_operating_system == true %}
            AND v.plugin_cpe like '%cpe:/o:%'
        {% endif %}
        {% if kwargs.is_operating_system == false %}
            AND v.plugin_cpe like '%cpe:/a:%'
        {% endif %}
        
        {% if kwargs.has_patch == true %}
            AND v.has_patch IS TRUE
        {% endif %}
        {% if kwargs.has_patch == false %}
            AND v.has_patch IS FALSE
        {% endif %}

        {% if kwargs.has_exploit == true %}
            AND v.has_exploit IS TRUE
        {% endif %}
        {% if kwargs.has_exploit == false %}
            AND v.has_patch IS FALSE
        {% endif %}

        {% if kwargs.published %}
            {{ days_to_today('v.plugin_published_date', 'CURRENT_DATE') }} > {{ kwargs.published }}
        {% endif %}
        
    GROUP BY v.asset_uuid
)

SELECT 
    '{{ kwargs.metric_id }}' AS metric_id,
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
LEFT JOIN crowdstrike_unremediated_vulns uv 
    ON uv.agent_id = cs.device_id
WHERE
    cs.serial_number is not null
    {% if kwargs.last_seen %}
        AND {{ days_to_today('cs.last_seen','cs.upload_timestamp') }} < {{ kwargs.last_seen }}
    {% endif %}

UNION ALL

SELECT 
    '{{ kwargs.metric_id }}' AS metric_id,
    ta.hostnames AS resource,
    ta.upload_timestamp,
    
    CASE 
        WHEN uv.vuln_count IS NULL THEN 1
        ELSE 0
    END AS compliance,

    CASE 
        WHEN uv.vuln_count IS NULL THEN 'No critical updates found'
        ELSE 'Patch or upgrade your system to remediate ' || uv.vuln_count || ' vulnerabilities.'
    END AS detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','tenable_assets') }} ta
LEFT JOIN unremediated_vulns_tenable uv 
    ON uv.asset_uuid = ta.id

    {% if kwargs.last_seen %}
    WHERE
    {{ days_to_today('ta.last_seen','ta.upload_timestamp') }} < {{ kwargs.last_seen }}
    {% endif %}

{% endmacro %} 