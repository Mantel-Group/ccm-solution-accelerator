{{
    config(
        materialized="table",
        tags=["mart"]
    )
}}

SELECT
    metric_id,
    framework_id,
    reference,
    framework,
    domain,
    sub_domain,
    control,
    {{ current_timestamp() }} as etl_timestamp,
    {{ current_date() }} as upload_date
from
    {{ ref('int_framework') }}
