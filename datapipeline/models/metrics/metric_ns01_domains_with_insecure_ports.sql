{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","domains"]
    )
}}

with domains as (
    select
        domain,
        max(upload_timestamp) as upload_timestamp
    FROM
    {{ source('source','domain_scan_results') }}
    WHERE
        domain is not null
    GROUP BY domain
)

select
    'NS01' as metric_id,
    d.domain as resource,
    d.upload_timestamp,
    
    case
        when port_80.result is true and redirect_80_to_443.result is true then 1
        when port_80.result is false then 1
        else 0
    end as compliance,

    case
        when port_80.result is true and redirect_80_to_443.result is true then 'Port 80 is active and redirecting to 443'
        when port_80.result is false then 'Port 80 is not active'
        when redirect_80_to_443.result is false then 'Port 80 is active but not redirecting to 443'
        else 'Something unexpected happened'
    end as detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM
    domains d
LEFT JOIN
    {{ source('source','domain_scan_results') }} port_80 on port_80.domain = d.domain and port_80.test = 'port_80'
LEFT JOIN
    {{ source('source','domain_scan_results') }} redirect_80_to_443 on redirect_80_to_443.domain = d.domain and redirect_80_to_443.test = 'redirect_80_to_443'