{{
    config(
        materialized="table",
        tags=["mart"]
    )
}}

WITH base_data as (
    SELECT 
        R.*,
        MAX(R.upload_date) OVER (PARTITION BY R.metric_id) as max_upload_date
    FROM {{ ref('int_metric_library_history') }} R
    INNER JOIN {{ ref('int_date_slices')}} SelectedDates ON
        CAST(SelectedDates.upload_timestamp as date) = R.upload_date
)

SELECT
  {{ dbt_utils.generate_surrogate_key(
    [
      "R.metric_id",
      "R.upload_date"
    ]
  ) }} as unique_sk_metric_id_upload_date,
  R.metric_id,
  R.upload_date,

  CASE
    WHEN L2.title is not null then L2.title
    else R.title
  END as title,

  CAST(R.in_production as BOOLEAN) as in_production,
  CAST(R.in_executive as BOOLEAN) as in_executive,
  CAST(R.in_management as BOOLEAN) as in_management,
  --CAST(R.in_control as BOOLEAN) as in_control,
  true as in_control,
  --CAST(R.in_individual as BOOLEAN) as in_individual,
  true as in_individual,
  R.slo_limit,
  R.slo_target,
  R.weight,
  R.description,
  R.upload_date = R.max_upload_date as is_latest,
  {{ current_timestamp() }} as etl_timestamp
from
    base_data R
left join {{ ref('int_metric_library') }} L2 on L2.metric_id = R.metric_id
