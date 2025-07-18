# Continuous Control Monitoring Data Model

## Overview

The Continuous Control Monitoring data model consists of four key materialized tables in the mart layer, each serving a specific purpose in tracking and analyzing organizational metrics and compliance.

## Table Schemas

### 1. mrt_v2_detail Table
Provides granular details about individual metrics and their compliance status.

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `upload_timestamp` | TIMESTAMP | Exact timestamp of the data upload |
| `upload_date` | DATE | Date of the upload |
| `metric_id` | STRING | Unique identifier for the metric |
| `owner` | STRING | Entity responsible for the metric |
| `resource` | STRING | Associated resource |
| `business_unit` | STRING | Organizational business unit |
| `team` | STRING | Team associated with the metric |
| `location` | STRING | Geographic or organizational location |
| `compliance` | FLOAT | Numeric representation of compliance percentage |
| `detail` | STRING | Specific details about the metric |
| `remediation` | STRING | Extracted remediation information, with special handling for updates and versions |
| `etl_timestamp` | TIMESTAMP | Timestamp of ETL processing |

### 2. mrt_v2_framework Table
Maps metrics to specific compliance frameworks and controls.

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `metric_id` | STRING | Unique identifier for the metric |
| `framework_id` | STRING | Identifier for the compliance framework |
| `reference` | STRING | Reference code or identifier |
| `framework` | STRING | Name of the compliance framework |
| `domain` | STRING | High-level domain of the framework |
| `sub_domain` | STRING | Specific sub-domain within the framework |
| `control` | STRING | Specific control within the framework |
| `etl_timestamp` | TIMESTAMP | Timestamp of ETL processing |
| `upload_date` | DATE | Date of the upload |

### 3. mrt_v2_metric_library Table
Comprehensive library of metrics, including their properties and categorizations.

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `unique_sk_metric_id_upload_date` | STRING | Surrogate key combining metric ID and upload date |
| `metric_id` | STRING | Unique identifier for the metric |
| `upload_date` | DATE | Date of the metric upload |
| `title` | STRING | Title of the metric (with fallback logic) |
| `in_production` | BOOLEAN | Indicates if the metric is in production |
| `in_executive` | BOOLEAN | Indicates executive-level visibility |
| `in_management` | BOOLEAN | Indicates management-level visibility |
| `in_control` | BOOLEAN | Indicates control-level metric |
| `in_individual` | BOOLEAN | Indicates individual-level metric |
| `slo_limit` | FLOAT | Service Level Objective limit |
| `slo_target` | FLOAT | Service Level Objective target |
| `weight` | FLOAT | Metric weight or importance |
| `metric_definition` | STRING | Description of the metric |
| `etl_timestamp` | TIMESTAMP | Timestamp of ETL processing |

### 4. mrt_v2_summary Table
Provides a summary of metrics across different organizational dimensions.

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `unique_sk_metric_id_upload_date` | STRING | Surrogate key combining metric ID and upload date |
| `metric_id` | STRING | Unique identifier for the metric |
| `upload_timestamp` | TIMESTAMP | Timestamp of the metric data |
| `upload_date` | DATE | Date of the metric data |
| `metric_numerator` | FLOAT | Numeric value for the metric numerator |
| `metric_denominator` | FLOAT | Numeric value for the metric denominator |
| `business_unit` | STRING | Organizational business unit |
| `team` | STRING | Team associated with the metric |
| `location` | STRING | Geographic or organizational location |
| `is_latest` | BOOLEAN | Indicates if this is the most recent record for the metric |
| `etl_timestamp` | TIMESTAMP | Timestamp of ETL processing |

## Data Processing Notes
- All tables are materialized as tables in the mart layer
- Timestamps and dates are automatically captured
- Surrogate keys are generated for unique identification
- Transformations include type casting, date handling, and special text processing

## Relationships
- The tables are interconnected through `metric_id`
- They provide a multi-dimensional view of organizational metrics, from granular details to high-level summaries
- Supports tracking of compliance across different frameworks, business units, and organizational levels

## Calculation Methodology
- Compliance is calculated as a percentage using the metric_numerator and metric_denominator
- Metrics can be filtered and aggregated across multiple dimensions:
  - Business Unit
  - Team
  - Location
  - Framework
  - Control Domain

## Dashboard Visualization Considerations
When recreating dashboards, consider:
- Filtering metrics by latest records using `is_latest`
- Aggregating compliance across different organizational levels
- Tracking metric trends over time using `upload_date`
- Mapping metrics to specific frameworks and controls

## Dashboard Visualization Methodology

### Overview Dashboard Calculation

The executive overview dashboard provides a comprehensive view of organizational compliance across multiple dimensions, utilizing weighted scoring and RAG (Red-Amber-Green) status indicators.

#### Key Calculation Principles
- Metrics are weighted based on their importance
- Scores are calculated using the formula: `SUM(metric_numerator) / SUM(metric_denominator) * weight`
- Only metrics marked as `in_production` and `in_executive` are included
- Scoring uses Service Level Objective (SLO) limits and targets

#### RAG Status Determination
- **Red**: Score is below the SLO limit
- **Amber**: Score is between the SLO limit and target
- **Green**: Score meets or exceeds the SLO target

### Dashboard Filters and Dimensions

#### Available Filters
1. **Business Unit**
   - Dynamically populated from `mrt_v2_summary`
   - Allows filtering metrics by organizational unit
   - Query: `SELECT DISTINCT business_unit FROM mrt_v2_summary WHERE is_latest IS TRUE`

2. **Team**
   - Dynamically populated from `mrt_v2_summary`
   - Allows filtering metrics by specific teams
   - Query: `SELECT DISTINCT team FROM mrt_v2_summary WHERE is_latest IS TRUE`

3. **Location**
   - Dynamically populated from `mrt_v2_summary`
   - Allows filtering metrics by geographic or organizational location
   - Query: `SELECT DISTINCT location FROM mrt_v2_summary WHERE is_latest IS TRUE`

4. **Framework**
   - Dynamically populated from `mrt_v2_framework`
   - Allows filtering metrics by compliance framework
   - Query: `SELECT DISTINCT framework FROM mrt_v2_framework`

### Visualization Reproduction Guidelines

#### 1. Aggregated Score Over Time Graph
- **Data Source**: Derived from `overview_query()`
- **X-Axis**: Upload Date
- **Y-Axis**: Weighted Compliance Score (0-100%)
- **Overlays**:
  - Green Dashed Line: SLO Target
  - Amber Dotted Line: SLO Limit
- **Color Coding**:
  - Red: Below SLO Limit
  - Amber: Between Limit and Target
  - Green: At or Above Target

#### 2. Business Unit Score Graph
- **Data Source**: Derived from `dimension_query('business_unit')`
- **X-Axis**: Compliance Score (0-100%)
- **Y-Axis**: Business Units
- **Horizontal Bar Chart**
- **Overlays**:
  - Green Dashed Line: SLO Target
  - Amber Dotted Line: SLO Limit
- **Color Coding**: Same as Aggregated Score Graph

#### 3. Cyber Domain Score Graph
- **Data Source**: Derived from `dimension_query('domain')`
- **X-Axis**: Compliance Score (0-100%)
- **Y-Axis**: Cyber Domains
- **Horizontal Bar Chart**
- **Overlays**:
  - Green Dashed Line: SLO Target
  - Amber Dotted Line: SLO Limit
- **Color Coding**: Same as Aggregated Score Graph

### Recommended BI Tool Configuration

When recreating this dashboard in another platform:
- Implement dynamic filtering across all three graphs
- Ensure weighted scoring calculation
- Maintain RAG status color scheme
- Include SLO target and limit lines
- Support drill-down and cross-filtering capabilities

### Performance Considerations
- Use materialized views or pre-aggregated tables
- Implement caching mechanisms
- Index frequently used columns in `mrt_v2_summary`, `mrt_v2_metric_library`, and `mrt_v2_framework`
