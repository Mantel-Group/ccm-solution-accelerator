{{
    config(
        materialized="table",
        tags=["intermediate"]
    )
}}

WITH DistinctDates AS (
  SELECT DISTINCT CAST(upload_timestamp AS DATE) AS upload_timestamp
  FROM 
    {{ ref('int_metric_summary') }}
  WHERE
    {{ days_to_today('upload_timestamp') }} < 366
), DatesBuckets AS (
  SELECT
    upload_timestamp,
    NTILE(12) OVER (ORDER BY upload_timestamp) AS bucket
  FROM DistinctDates
)

SELECT 
  MAX(upload_timestamp) AS upload_timestamp
FROM
    DatesBuckets
GROUP BY
    bucket
ORDER BY
    upload_timestamp DESC
