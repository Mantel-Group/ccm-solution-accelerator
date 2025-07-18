{{
    config(
        materialized="table",
        tags=["intermediate"]
    )
}}

select
    m.upload_timestamp,
    cast(m.upload_timestamp as date) as upload_date,
    m.metric_id,
    m.resource,
    CASE
        when X.metric_id is not null then 1
        else m.compliance
    END as compliance,
    CASE
        WHEN X.metric_id is not null then 'Exception - approved automatically until ' || X.expiry_date
        else m.detail
    END as detail,
    L.title,
    --L.domain_category as cyber_category,
    --L.domain as cyber_domain,
    L.slo_target,
    L.slo_limit,
    --L.slo_type,
    L.weight,
    --L.accountable,
    --L.help_text,
    --L.url,
    --L.in_board,
    L.in_production,
    L.in_executive,
    L.in_management,
    --L.in_control,
    --L.in_individual,
    --L.in_slack_alert,

    coalesce(a.business_unit,'undefined') as business_unit,
    coalesce(a.team,'undefined') as team,
    coalesce(a.location,'undefined') as location,
    coalesce(a.owner,'undefined') as owner
from
    {{ ref('int_metrics_combined') }} m
inner join {{ ref('int_metric_library') }} L on L.metric_id = M.metric_id
left join {{ ref('int_asset_register') }} A on upper(A.resource) = upper(m.resource) and lower(A.resource_type) = lower(L.resource_type)
left join {{ ref('int_exceptions') }} X on X.metric_id = M.metric_id and A.resource = X.resource AND X.expiry_date >= {{ current_date() }}

