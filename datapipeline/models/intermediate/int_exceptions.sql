{{
    config(
        materialized="table",
        tags=["intermediate"]
    )
}}

select
    metric_id,
    resource,
    cast(expiry_date as date) as expiry_date
from
    {{ ref('seed__exceptions') }}

