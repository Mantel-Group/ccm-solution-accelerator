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

select
    'IM01'   metric_id,
    profile_login as resource,
    upload_timestamp,
    case
        when {{ days_to_today('created','upload_timestamp') }} < 90 then 1
        when {{ days_to_today('last_login','upload_timestamp') }} < 90 then 1
        else 0
    end compliance,
    case
        when {{ days_to_today('created','upload_timestamp') }} < 90 then 'New account created in the last 90 days : ' || created
        when {{ days_to_today('last_login','upload_timestamp') }} < 90 then 'Last login within 90 days : ' || last_login    
        else 'Last login more than 90 days ago : ' || last_login
    end detail,
    {{ current_timestamp() }} as etl_timestamp
from
    {{ source('source','okta_users') }}
where
    status = 'ACTIVE'