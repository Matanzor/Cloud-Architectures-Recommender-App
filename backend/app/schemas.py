from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


USE_CASES = [
    "web_application", "public_api", "ecommerce", "real_time_analytics",
    "batch_processing", "event_processing", "media_delivery", "internal_tool",
    "iot_ingestion", "ml_inference"
]
SCALES = ["small", "medium", "large"]
TRAFFIC_PATTERNS = ["steady", "bursty", "spiky", "scheduled", "unpredictable"]
LATENCY_LEVELS = ["low", "medium", "high"]
PROCESSING_STYLES = ["request_response", "event_driven", "batch", "streaming"]
DATA_INTENSITY = ["low", "medium", "high"]
AVAILABILITY = ["standard", "high", "critical"]
OPS_PREFERENCE = ["managed_services", "balanced", "self_managed_ok"]
BUDGET_SENSITIVITY = ["low", "medium", "high"]


class RecommendRequest(BaseModel):
    use_case: Literal[
        "web_application", "public_api", "ecommerce", "real_time_analytics",
        "batch_processing", "event_processing", "media_delivery", "internal_tool",
        "iot_ingestion", "ml_inference"
    ]
    scale: Literal["small", "medium", "large"]
    traffic_pattern: Literal["steady", "bursty", "spiky", "scheduled", "unpredictable"]
    latency_sensitivity: Literal["low", "medium", "high"]
    processing_style: Literal["request_response", "event_driven", "batch", "streaming"]
    data_intensity: Literal["low", "medium", "high"]
    availability_requirement: Literal["standard", "high", "critical"]
    ops_preference: Literal["managed_services", "balanced", "self_managed_ok"]
    budget_sensitivity: Literal["low", "medium", "high"]


class ResourceItem(BaseModel):
    resource_type: str
    resource_name: str
    count: int = 1


class ArchitectureMetadata(BaseModel):
    use_case: str
    scale: str
    traffic_pattern: str
    latency_sensitivity: str
    processing_style: str
    data_intensity: str
    availability_requirement: str
    ops_preference: str
    budget_sensitivity: str


class ArchitectureOut(BaseModel):
    id: str
    source_url: str
    title: str
    description: str
    scraped_at: datetime
    resources: list[ResourceItem]
    metadata: ArchitectureMetadata


class ArchitectureListItem(BaseModel):
    id: str
    title: str
    source_url: str
    scraped_at: datetime
    metadata: ArchitectureMetadata


class RecommendationResult(BaseModel):
    architecture: ArchitectureOut
    score: float
    explanation: str
