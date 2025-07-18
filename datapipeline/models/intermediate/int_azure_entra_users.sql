{{
    config(
        materialized="table",
        tags=["intermediate"]
    )
}}

with last_login as (
    select
        user_principal_name,
        max(created_date_time) as created_date_time
    from
        {{ source('source','azure_entra_users_signin') }}
    group by
        user_principal_name
)

select
    U.id,
    U.display_name,
    U.given_name,
    U.surname,
    U.user_principal_name,
    U.mail,
    U.job_title,
    U.department,
    U.mobile_phone,
    U.business_phones,
    U.office_location,
    U.preferred_language,
    U.account_enabled,
    U.user_type,
    U.created_date_time,
    U.last_password_change_date_time,
    U.tenancy,
    U.upload_timestamp,
    last_login.created_date_time as last_login_date_time
FROM
    {{ source('source','azure_entra_users') }} U
LEFT JOIN last_login on last_login.user_principal_name = U.user_principal_name