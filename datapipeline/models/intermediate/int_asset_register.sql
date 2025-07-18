{{
    config(
        materialized="table",
        tags=["intermediate"]
    )
}}

SELECT
    lower(resource_type) as resource_type,
    upper(resource) as resource,
    business_unit,
    team,
    location,
    owner,
    cast(active as boolean) as active
FROM
    {{ ref('seed__asset_register') }}