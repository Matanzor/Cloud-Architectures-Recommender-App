
import json
import re

from app.config import settings

AWS_SERVICES = [
    "EC2", "Lambda", "S3", "RDS", "DynamoDB", "API Gateway", "CloudFront",
    "ECS", "EKS", "Fargate", "SQS", "SNS", "EventBridge", "Kinesis",
    "Glue", "EMR", "Athena", "Redshift", "ElastiCache", "Aurora",
    "CloudWatch", "WAF", "MediaConvert", "IoT Core", "SageMaker", "ALB",
]

KEYWORD_MAP = {
    "use_case": {
        "web_application": ["web app", "web application", "website", "spa"],
        "public_api": ["public api", "rest api", "http api"],
        "ecommerce": ["ecommerce", "e-commerce", "shop", "store"],
        "real_time_analytics": ["real-time", "realtime", "streaming analytics"],
        "batch_processing": ["batch", "etl", "data pipeline"],
        "event_processing": ["event-driven", "event driven", "events"],
        "media_delivery": ["media", "video", "cdn", "streaming"],
        "internal_tool": ["internal", "admin", "tool"],
        "iot_ingestion": ["iot", "device", "telemetry", "sensors"],
        "ml_inference": ["ml", "machine learning", "inference", "sagemaker"],
    },
    "ops_preference": {
        "managed_services": ["serverless", "lambda", "managed", "fargate"],
        "balanced": ["ecs", "eks", "container"],
        "self_managed_ok": ["ec2", "self-managed", "on-prem"],
    },
    "processing_style": {
        "request_response": ["api", "rest", "http", "request"],
        "event_driven": ["event", "eventbridge", "sqs", "sns"],
        "batch": ["batch", "scheduled", "cron"],
        "streaming": ["stream", "kinesis", "real-time"],
    },
    "data_intensity": {
        "high": ["big data", "petabyte", "terabyte", "analytics", "emr", "redshift"],
        "medium": ["database", "rds", "dynamodb"],
        "low": ["simple", "small", "minimal"],
    },
    "latency_sensitivity": {
        "high": ["real-time", "low latency", "millisecond", "critical"],
        "medium": ["responsive", "fast"],
        "low": ["batch", "async", "overnight"],
    },
    "availability_requirement": {
        "critical": ["high availability", "ha", "multi-az", "99.99"],
        "high": ["reliable", "resilient", "availability"],
        "standard": ["single", "dev", "internal"],
    },
    "scale": {
        "large": ["scale", "high traffic", "millions", "petabyte"],
        "medium": ["moderate", "growing", "medium"],
        "small": ["small", "low traffic", "startup", "prototype"],
    },
    "traffic_pattern": {
        "bursty": ["burst", "spike", "variable", "seasonal"],
        "steady": ["consistent", "predictable", "steady"],
        "spiky": ["spike", "unpredictable", "viral"],
        "scheduled": ["scheduled", "cron", "batch", "nightly"],
        "unpredictable": ["unpredictable", "variable", "real-time"],
    },
    "budget_sensitivity": {
        "high": ["cost-effective", "cheap", "budget", "minimal cost"],
        "medium": ["balanced", "reasonable"],
        "low": ["enterprise", "scale", "performance"],
    },
}


def extract_resources(text: str) -> list[dict]:
    text_upper = text.upper()
    found = []
    for svc in AWS_SERVICES:
        pattern = re.compile(rf"\b{re.escape(svc)}\b", re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            found.append({
                "resource_type": svc,
                "resource_name": svc,
                "count": len(matches),
            })
    if not found:
        found.append({"resource_type": "Unknown", "resource_name": "Generic", "count": 1})
    return found


VALID_VALUES = {
    "use_case": ["web_application", "public_api", "ecommerce", "real_time_analytics", "batch_processing", "event_processing", "media_delivery", "internal_tool", "iot_ingestion", "ml_inference"],
    "scale": ["small", "medium", "large"],
    "traffic_pattern": ["steady", "bursty", "spiky", "scheduled", "unpredictable"],
    "latency_sensitivity": ["low", "medium", "high"],
    "processing_style": ["request_response", "event_driven", "batch", "streaming"],
    "data_intensity": ["low", "medium", "high"],
    "availability_requirement": ["standard", "high", "critical"],
    "ops_preference": ["managed_services", "balanced", "self_managed_ok"],
    "budget_sensitivity": ["low", "medium", "high"],
}


def _infer_metadata_with_ai(text: str, resources: list[dict]) -> dict | None:
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resource_list = [r["resource_type"] for r in resources]
        prompt = f"""Extract cloud architecture metadata from this text. AWS services used: {resource_list}.

Text (excerpt):
{text[:4000]}

Return a JSON object with exactly these keys, using only the allowed values:
- use_case: web_application, public_api, ecommerce, real_time_analytics, batch_processing, event_processing, media_delivery, internal_tool, iot_ingestion, ml_inference
- scale: small, medium, large
- traffic_pattern: steady, bursty, spiky, scheduled, unpredictable
- latency_sensitivity: low, medium, high
- processing_style: request_response, event_driven, batch, streaming
- data_intensity: low, medium, high
- availability_requirement: standard, high, critical
- ops_preference: managed_services, balanced, self_managed_ok
- budget_sensitivity: low, medium, high

Return only valid JSON, no other text."""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        data = json.loads(content)
        result = {}
        for field, valid in VALID_VALUES.items():
            val = data.get(field, "").lower().replace(" ", "_")
            if val in valid:
                result[field] = val
            else:
                return None
        return result
    except Exception:
        return None


def infer_metadata(text: str, resources: list[dict]) -> tuple[dict, str]:
    ai_result = _infer_metadata_with_ai(text, resources)
    if ai_result:
        return ai_result, "ai"

    text_lower = text.lower()
    resource_types = [r["resource_type"].lower() for r in resources]
    combined = text_lower + " " + " ".join(resource_types)

    defaults = {
        "use_case": "web_application",
        "scale": "medium",
        "traffic_pattern": "steady",
        "latency_sensitivity": "medium",
        "processing_style": "request_response",
        "data_intensity": "medium",
        "availability_requirement": "standard",
        "ops_preference": "managed_services",
        "budget_sensitivity": "medium",
    }

    metadata = {}
    for field, options in KEYWORD_MAP.items():
        best = defaults.get(field, list(options.keys())[0])
        best_score = 0
        for value, keywords in options.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > best_score:
                best_score = score
                best = value
        metadata[field] = best
    return metadata, "rule_based"
