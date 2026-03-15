from app.schemas import RecommendRequest


def score_architecture(arch: dict, req: RecommendRequest) -> tuple[float, str]:
    meta = arch.get("metadata", {})
    if not meta:
        return 0.0, []

    weights = {
        "use_case": 3,
        "scale": 2,
        "availability_requirement": 2,
        "traffic_pattern": 1,
        "latency_sensitivity": 1,
        "processing_style": 1,
        "data_intensity": 1,
        "ops_preference": 1,
        "budget_sensitivity": 1,
    }

    req_dict = req.model_dump()
    score = 0.0
    matched = []

    for field, weight in weights.items():
        arch_val = meta.get(field)
        req_val = req_dict.get(field)
        if arch_val == req_val:
            score += weight
            matched.append(field.replace("_", " "))

    if not matched:
        return 0.0, "No direct matches."

    explanation = "Matches your " + ", ".join(matched) + "."
    return score, explanation
