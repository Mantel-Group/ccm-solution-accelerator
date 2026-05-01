def build_placeholders(filters: dict, prefix: str = "") -> str:
    if not filters:
        return ""
    conditions = [f"{prefix}{field} = :{field}" for field in filters]
    return "AND " + " AND ".join(conditions)


def overview_query(filters: dict) -> str:
    placeholders = build_placeholders(filters)
    return f"""
SELECT
    Q1.upload_date,
    SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) AS score,
    SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) AS slo_limit,
    SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) AS slo_target,
    CASE
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) < SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) THEN 'red'
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) >= SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) THEN 'green'
        ELSE 'amber'
    END AS rag
FROM (
    SELECT
        S.upload_date,
        S.metric_id,
        SUM(S.metric_numerator) / SUM(S.metric_denominator) * AVG(L.weight) AS weighted_score,
        L.slo_limit * AVG(L.weight) AS weighted_slo_limit,
        L.slo_target * AVG(L.weight) AS weighted_slo_target,
        L.weight
    FROM mrt_v2_summary S
    INNER JOIN mrt_v2_metric_library L ON L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
    INNER JOIN mrt_v2_framework F ON F.metric_id = S.metric_id
    WHERE L.in_production IS true AND L.in_executive IS true
    {placeholders}
    GROUP BY S.upload_date, S.metric_id, L.slo_limit, L.slo_target, L.weight
) Q1
GROUP BY Q1.upload_date
ORDER BY Q1.upload_date ASC
"""


def dimension_query(dimension: str, filters: dict) -> str:
    placeholders = build_placeholders(filters)
    return f"""
SELECT
    Q1.{dimension},
    SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) AS score,
    SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) AS slo_limit,
    SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) AS slo_target,
    CASE
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) < SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) THEN 'red'
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) >= SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) THEN 'green'
        ELSE 'amber'
    END AS rag
FROM (
    SELECT
        {dimension},
        S.metric_id,
        SUM(S.metric_numerator) / SUM(S.metric_denominator) * AVG(L.weight) AS weighted_score,
        L.slo_limit * AVG(L.weight) AS weighted_slo_limit,
        L.slo_target * AVG(L.weight) AS weighted_slo_target,
        L.weight
    FROM mrt_v2_summary S
    INNER JOIN mrt_v2_metric_library L ON L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
    INNER JOIN mrt_v2_framework F ON F.metric_id = S.metric_id
    WHERE L.in_production IS true AND L.in_executive IS true AND S.is_latest IS true
    {placeholders}
    GROUP BY {dimension}, S.metric_id, L.slo_limit, L.slo_target, L.weight
) Q1
GROUP BY Q1.{dimension}
"""


def metrics_query(filters: dict) -> str:
    placeholders = build_placeholders(filters)
    return f"""
SELECT
    S.upload_date,
    S.metric_id,
    L.title,
    SUM(S.metric_numerator) / SUM(S.metric_denominator) AS score,
    L.slo_limit,
    L.slo_target,
    L.weight,
    CASE
        WHEN SUM(S.metric_numerator) / SUM(S.metric_denominator) < L.slo_limit THEN 'red'
        WHEN SUM(S.metric_numerator) / SUM(S.metric_denominator) >= L.slo_target THEN 'green'
        ELSE 'amber'
    END AS rag
FROM mrt_v2_summary S
INNER JOIN mrt_v2_metric_library L ON L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
INNER JOIN mrt_v2_framework F ON F.metric_id = S.metric_id
WHERE L.in_production IS true AND L.in_management IS true AND S.is_latest = true
{placeholders}
GROUP BY S.upload_date, S.metric_id, L.slo_limit, L.title, L.slo_target, L.weight
"""


_METRIC_DETAIL_PREFIXES = {"metric_id": "L.", "framework": "F."}


def metric_detail_query(filters: dict) -> str:
    conditions = []
    for field in filters:
        prefix = _METRIC_DETAIL_PREFIXES.get(field, "")
        conditions.append(f"{prefix}{field} = :{field}")
    placeholders = "AND " + " AND ".join(conditions) if conditions else ""
    return f"""
SELECT
    Q1.upload_date,
    SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) AS score,
    SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) AS slo_limit,
    SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) AS slo_target,
    CASE
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) < SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) THEN 'red'
        WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) >= SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) THEN 'green'
        ELSE 'amber'
    END AS rag
FROM (
    SELECT
        S.upload_date,
        S.metric_id,
        SUM(S.metric_numerator) / SUM(S.metric_denominator) * AVG(L.weight) AS weighted_score,
        L.slo_limit * AVG(L.weight) AS weighted_slo_limit,
        L.slo_target * AVG(L.weight) AS weighted_slo_target,
        L.weight
    FROM mrt_v2_summary S
    INNER JOIN mrt_v2_metric_library L ON L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
    INNER JOIN mrt_v2_framework F ON F.metric_id = S.metric_id
    WHERE L.in_production IS true AND L.in_executive IS true
    {placeholders}
    GROUP BY S.upload_date, S.metric_id, L.slo_limit, L.slo_target, L.weight
) Q1
GROUP BY Q1.upload_date
ORDER BY Q1.upload_date ASC
"""


_DETAIL_COLUMNS = {"metric_id", "business_unit", "team", "location"}


def detail_query(filters: dict) -> str:
    applicable = {k: v for k, v in filters.items() if k in _DETAIL_COLUMNS}
    placeholders = build_placeholders(applicable)
    return f"""
SELECT
    upload_date,
    resource,
    owner,
    compliance,
    detail
FROM mrt_v2_detail
WHERE compliance < 10
{placeholders}
ORDER BY compliance
"""
