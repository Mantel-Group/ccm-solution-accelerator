{{
    config(
        materialized="table",
        partition_by={
            "field": "upload_timestamp",
            "data_type": "datestamp",
            "granularity": "day",
        },
        tags=["metric","knowbe4"]
    )
}}

with phishing_stats as (
    select
        user_email,
        upload_timestamp,
        count(*) as total_delivered,
        sum(case when clicked_at IS NOT NULL then 1 else 0 end) as total_clicked,
        max(case when clicked_at IS NOT NULL then clicked_at else null end) as last_clicked_date,
        max(case when reported_at IS NOT NULL then reported_at else null end) as last_reported_date
    from
        {{ source('source','knowbe4_pst_recipients') }}
    where
        delivered_at IS NOT NULL
        and {{ days_to_today('delivered_at','upload_timestamp') }} <= 30
    group by user_email, upload_timestamp
)
select
    'US03' as metric_id,
    user_email as resource,
    upload_timestamp,
    case
        when total_delivered > 0 then 1.0 - (cast(total_clicked as float) / cast(total_delivered as float))
        else 1.0
    end as compliance,
    case
        when total_delivered = 0 then 'No phishing emails delivered in the last 30 days'
        when total_clicked = 0 then 'User did not click any phishing emails in the last 30 days (' || total_delivered || ' delivered)'
        when total_clicked > 0 then 'User clicked ' || total_clicked || ' of ' || total_delivered || ' phishing emails in the last 30 days (last clicked: ' || last_clicked_date || ')'
        else 'Unknown status'
    end as detail,
    {{ current_timestamp() }} as etl_timestamp
from
    phishing_stats
where
    user_email IS NOT NULL
