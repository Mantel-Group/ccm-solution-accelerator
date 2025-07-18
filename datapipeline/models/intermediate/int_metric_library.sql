{{
    config(
        materialized="table",
        tags=["intermediate","metric_library"]
    )
}}

SELECT
    metric_id,
    title,
    in_production,
    in_executive,
    in_management,
    {{ cast_float('slo_target') }} as slo_target,
    {{ cast_float('slo_limit') }} as slo_limit,
    {{ cast_float('weight') }} as weight,
    description,
    resource_type,
    framework,
    {{ current_timestamp() }} as etl_timestamp,
    {{ current_date() }} as upload_date
from
    {{ ref('seed__metric_library') }}
