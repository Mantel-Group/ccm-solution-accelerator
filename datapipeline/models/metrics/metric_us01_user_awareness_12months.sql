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

with awareness as (
    select
        email,
        max(completion_date) as completion_date
    from
        {{ source('source','knowbe4_enrollments') }}
    where
     status = 'Passed'
    group by email
)
select
    'US01'   metric_id,
    profile_login as resource,
    upload_timestamp,
    case
        when {{ days_to_today('A.completion_date','upload_timestamp') }} < 365 then 1
        else 0
    end compliance,
    case
        when {{ days_to_today('A.completion_date','upload_timestamp') }} < 365 then 'Awareness training completed in the last 12 months on ' || A.completion_date
        when {{ days_to_today('A.completion_date','upload_timestamp') }} >= 365 then 'Awareness training completed more than 12 months ago on ' || A.completion_date
        else 'Awarenss training never completed yet'
    end detail,
    {{ current_timestamp() }} as etl_timestamp
from
    {{ source('source','okta_users') }} U
left join awareness A on A.email = U.profile_login
where
    profile_login is not null AND
    status = 'ACTIVE'