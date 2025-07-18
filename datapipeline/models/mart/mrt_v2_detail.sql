{{
    config(
        materialized="table",
        tags=["mart"]
    )
}}

select
    d.upload_timestamp,
    CAST(d.upload_timestamp as date) as upload_date,
    d.metric_id,
    d.owner,
    d.resource,
    d.business_unit,
    d.team,
    d.location,
    {{ cast_float('d.compliance') }} as compliance,
    d.detail,
    CASE
        WHEN d.detail like 'Update Apple Mac OS%' THEN 'Update Apple Mac OS'
        WHEN STRPOS(d.detail, 'to version') > 0
            THEN SUBSTR(d.detail, 1, STRPOS(d.detail, 'to version') - 1)
        WHEN STRPOS(d.detail, 'to a version') > 0
            THEN SUBSTR(d.detail, 1, STRPOS(d.detail, 'to a version') - 1)
        ELSE d.detail
    END AS remediation,
    {{ current_timestamp() }} as etl_timestamp
from
    {{ ref('int_metrics_merged') }} d
