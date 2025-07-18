{% macro current_timestamp() %}
    {%- if target.type == "bigquery" %} CURRENT_TIMESTAMP() {%- endif %}
    {%- if target.type == "duckdb"   %} CURRENT_TIMESTAMP   {%- endif %}
    {%- if target.type == "postgres" %} CURRENT_TIMESTAMP   {%- endif %}
    
{% endmacro %}

{% macro split_field(field,delim,id) %}
    {%- if target.type == "postgres" %}  ,          unnest(string_to_array( {{ field }}, '{{ delim }}')) AS    {{ id }}   {%- endif %}
    {%- if target.type == "duckdb"   %}  ,          unnest(string_split(    {{ field }}, '{{ delim }}')) AS t( {{ id }} ) {%- endif %}
    {%- if target.type == "bigquery" %}  cross join unnest(split(           {{ field }}, '{{ delim }}')) as    {{ id }}   {%- endif %}
{% endmacro %}

{% macro current_date() %}
    {%- if target.type == "postgres" %} CURRENT_DATE    {%- endif %}
    {%- if target.type == "duckdb"   %} CURRENT_DATE()  {%- endif %}
    {%- if target.type == "bigquery" %} CURRENT_DATE()  {%- endif %}
{% endmacro %}

{% macro cast_float(field) %}
    {% if target.type == "postgres" %}  cast({{ field }} as float)     {%- endif %}
    {% if target.type == "duckdb"   %}  cast({{ field }} as DOUBLE)    {%- endif %}
    {% if target.type == "bigquery" %}  cast({{ field }} as FLOAT64)   {% endif %}
{% endmacro %}

{% macro cast_string(field) %}
    {% if target.type == "postgres" %}  cast({{ field }} as text)     {%- endif %}
    {% if target.type == "postgres" %}  cast({{ field }} as varchar)  {%- endif %}
    {% if target.type == "bigquery" %}  cast({{ field }} as string)   {% endif %}
{% endmacro %}



{% macro days_to_today(field,field2 = None) %}
    {% if field2 == None %}
        {%- if target.type == "postgres" %} date_part('day', current_date - {{ field }} )               {%- endif %}
        {%- if target.type == "duckdb"   %} datediff('day', {{ field }}, current_date)                  {%- endif %}
        {%- if target.type == "bigquery" %} date_diff(current_date(), cast({{ field }} as date), day)   {%- endif %}
    {% else %}
        {%- if target.type == "postgres" %} date_part('day', {{ field2 }} - {{ field }} )                           {%- endif %}
        {%- if target.type == "duckdb"  -%} datediff('day', {{ field }}, {{ field2 }})                              {%- endif %}
        {%- if target.type == "bigquery" %} date_diff(cast({{ field2 }} as date), cast({{ field }} as date), day)   {%- endif %}
    {% endif %}
{% endmacro %}






