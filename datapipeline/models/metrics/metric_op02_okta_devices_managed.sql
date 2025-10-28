{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","okta"]
    )
}}

SELECT
    'OP02' AS metric_id,
    COALESCE(u.profile_email, u.profile_login, du.user_id) AS resource,
    d.upload_timestamp,

    CASE
        WHEN du.managementstatus = 'MANAGED' THEN 1
        ELSE 0
    END AS compliance,

    CASE
        WHEN du.managementstatus = 'MANAGED' THEN
            COALESCE(d.profile_platform, 'Unknown Platform') ||
            CASE
                WHEN d.profile_manufacturer IS NOT NULL AND d.profile_model IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ' ' || d.profile_model || ')'
                WHEN d.profile_manufacturer IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ')'
                WHEN d.profile_model IS NOT NULL
                THEN ' (' || d.profile_model || ')'
                ELSE ''
            END
        WHEN du.managementstatus IS NOT NULL THEN
            du.managementstatus || ' - ' ||
            COALESCE(d.profile_platform, 'Unknown Platform') ||
            CASE
                WHEN d.profile_manufacturer IS NOT NULL AND d.profile_model IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ' ' || d.profile_model || ')'
                WHEN d.profile_manufacturer IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ')'
                WHEN d.profile_model IS NOT NULL
                THEN ' (' || d.profile_model || ')'
                ELSE ''
            END
        ELSE
            'Device management status unknown - ' ||
            COALESCE(d.profile_platform, 'Unknown Platform') ||
            CASE
                WHEN d.profile_manufacturer IS NOT NULL AND d.profile_model IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ' ' || d.profile_model || ')'
                WHEN d.profile_manufacturer IS NOT NULL
                THEN ' (' || d.profile_manufacturer || ')'
                WHEN d.profile_model IS NOT NULL
                THEN ' (' || d.profile_model || ')'
                ELSE ''
            END
    END AS detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM {{ source('source','okta_devices') }} d
LEFT JOIN {{ source('source','okta_device_users') }} du ON d.id = du.device_id
LEFT JOIN {{ source('source','okta_users') }} u ON du.user_id = u.id
WHERE
    d.id IS NOT NULL
    AND d.lastupdated IS NOT NULL
    AND {{ days_to_today('d.lastupdated','d.upload_timestamp') }} <= 30
    AND u.profile_login IS NOT NULL
