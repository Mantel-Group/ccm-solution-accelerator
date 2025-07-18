{{
    config(
        materialized="incremental",
        on_schema_change="sync_all_columns",
        tags=["intermediate","metric_library"]
    )
}}

SELECT
    metric_id,
    title,
    in_production,
    in_executive,
    in_management,
    slo_target,
    slo_limit,
    weight,
    description,
    resource_type,
    framework,
    etl_timestamp,
    upload_date,
    {{ dbt_utils.generate_surrogate_key(
        [
        "metric_id",
        "upload_date"
        ]
    ) }} as unique_sk_metric_id_upload_date
from
    {{ ref('int_metric_library') }}
{% if is_incremental() %}
    WHERE {{ current_date() }} > (SELECT MAX(upload_date) FROM {{ this }})
{% endif %}