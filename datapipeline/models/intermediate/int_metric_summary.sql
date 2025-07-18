{{
    config(
        materialized="incremental",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "timestamp",
            "granularity": "day",
        },
        tags=["intermediate"]
    )
}}

select
    m.metric_id,
    m.upload_timestamp,
    cast(m.upload_timestamp as date) upload_date,
    sum(m.compliance) metric_numerator,
    count(m.compliance) metric_denominator,
    m.business_unit,
    m.team,
    m.location
from
    {{ ref('int_metrics_merged') }} m
{% if is_incremental() %}
    WHERE cast(m.upload_timestamp as date) > (SELECT MAX(upload_date) FROM {{ this }})
{% endif %}
group by
    m.metric_id,
    m.upload_timestamp,
    m.business_unit,
    m.team,
    m.location