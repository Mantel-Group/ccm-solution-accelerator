{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","entra"]
    )
}}

SELECT
    'IM02'   metric_id,
    user_principal_name as resource,
    upload_timestamp,
    case
        when {{ days_to_today('created_date_time','upload_timestamp') }} < 365 then 1
        when {{ days_to_today('last_password_change_date_time','upload_timestamp') }} < 365 then 1
        else 0
    end compliance,
    case
        when {{ days_to_today('created_date_time','upload_timestamp') }} < 365 then 'New account created in the last 365 days : ' || created_date_time
        when {{ days_to_today('last_password_change_date_time','upload_timestamp') }} < 365 then 'Password changed within the last 365 days : ' || last_password_change_date_time
        else 'Password changed more than 365 days ago : ' || last_password_change_date_time
    end detail,
    {{ current_timestamp() }} as etl_timestamp
from
    {{ ref('int_azure_entra_users') }}
where
    user_principal_name is not null and
    account_enabled is true