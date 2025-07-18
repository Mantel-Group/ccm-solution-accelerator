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

SELECT
    'IM02'   metric_id,
    profile_login as resource,
    upload_timestamp,
    case
        when {{ days_to_today('created','upload_timestamp') }} < 365 then 1
        when {{ days_to_today('password_changed','upload_timestamp') }} < 365 then 1
        else 0
    end compliance,
    case
        when {{ days_to_today('created','upload_timestamp') }} < 365 then 'New account created in the last 365 days : ' || created
        when {{ days_to_today('password_changed','upload_timestamp') }} < 365 then 'Password changed within the last 365 days : ' || password_changed
        else 'Password changed more than 365 days ago : ' || password_changed
    end detail,
    {{ current_timestamp() }} as etl_timestamp
FROM
    {{ source('source','okta_users') }}
WHERE
    profile_login is not null AND
    status = 'ACTIVE'