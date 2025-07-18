{{
    config(
        materialized="table",
        tags=["mart"]
    )
}}

WITH maxdate as (
    select
        metric_id,
        max(upload_timestamp) as maxdate
    from
        {{ ref('int_metric_summary') }}
    group by metric_id
)

SELECT
  {{ dbt_utils.generate_surrogate_key(
    [
        "S.metric_id",
        "S.upload_date"
    ]
  ) }} as unique_sk_metric_id_upload_date,
  S.metric_id,
  S.upload_timestamp,
  S.upload_date,
  {{ cast_float('S.metric_numerator') }} as metric_numerator,
  {{ cast_float('S.metric_denominator') }} as metric_denominator,
  S.business_unit,
  S.team,
  S.location,
  maxdate.maxdate is not null as is_latest,
  {{ current_timestamp() }} as etl_timestamp
from
    {{ ref('int_metric_summary') }} S
inner join {{ ref('int_date_slices') }} SelectedDates on SelectedDates.upload_timestamp = cast(S.upload_timestamp as date)
left join maxdate on maxdate.metric_id = S.metric_id and maxdate.maxdate = s.upload_timestamp
