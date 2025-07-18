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
    'NS02' as metric_id,
    d.domain as resource,
    d.upload_timestamp,
    
    case
        when ssl_certificate_valid.result is true then 1
        else 0
    end as compliance,

    case
        when ssl_certificate_valid.result is true then 'SSL Certificate is valid'
        when ssl_certificate_valid.result is false then 'SSL Certificate is invalid or missing'
        else 'Something unexpected happened'
    end as detail,

    {{ current_timestamp() }} AS etl_timestamp

FROM
    domains d
INNER JOIN
    {{ source('source','domain_scan_results') }} port_443 on port_443.domain = d.domain and port_443.test = 'port_443' and port_443.result is true
LEFT JOIN
    {{ source('source','domain_scan_results') }} ssl_certificate_valid on ssl_certificate_valid.domain = d.domain and ssl_certificate_valid.test = 'ssl_certificate_valid'