{{
  config(
      materialized = "table",
      tags = ["intermediate"]
  )
}}


    select
        metric_id,
        framework_id,
         f._framework_ref      as reference,
    f.framework,
    f.domain,
    f.sub_domain,
    f.control,
    {{ current_timestamp() }}  as etl_timestamp
    from {{ ref('seed__metric_library') }} l
    {{ split_field('framework', ';', 'framework_id') }}
left join {{ ref('seed__metric_framework') }}  f
        on f.id = framework_id


