import re

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


def infer_metadata(text: str, resources: list[dict]) -> dict:
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
    return metadata
