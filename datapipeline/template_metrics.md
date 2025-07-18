{%- macro icon(text) -%}
    {%- if text == 'true' -%}
        ![yes](https://img.shields.io/badge/YES-0000F0)
    {%- elif text == 'false' -%}
        ![no](https://img.shields.io/badge/NO-0F00)
    {%- else -%}
        {{ text }}
    {%- endif -%}
{%- endmacro -%}
# Continuous Controls Monitoring - Metric Library

## List of metrics

| Metric ID                | Description      | Executive | Management |
|--------------------------|------------------|-----------|------------|
{% for x in data -%}
| **{{ x['metric_id'] }}** | {{ x['title'] }} | {{ icon(x['in_executive']) }} | {{ icon(x['in_management']) }} |
{% endfor %}

## Metric Details

{%- for x in data %}
### {{ x['metric_id'] }} - {{ x['title'] }}

#### Description

{{ x['description'] }}

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `{{ x['metric_id'] }}`                                                               |
| **SLO**           | {{ (x['slo_limit'] * 100) | round(2) }}% - {{ (x['slo_target'] * 100) | round(2) }}% |
| **Weight**        | {{ x['weight'] }}                                                                    |
| **Resource Type** | {{ x['resource_type'] }}                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
{% for f in x['references'] -%}
|{{ f['framework'] }}|{{ f['ref'] }}|{{ f['domain'] }}|{{ f['control'] }}|
{% endfor %}

{% endfor %}