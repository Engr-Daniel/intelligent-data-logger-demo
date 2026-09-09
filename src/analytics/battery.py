def battery_runway(current_soc_pct: float, usable_capacity_kwh: float, current_load_w: float, min_soc_pct: float = 10) -> dict:
    available_frac = max(0.0, (current_soc_pct - min_soc_pct) / 100)
    available_kwh = usable_capacity_kwh * available_frac
    hours = None if current_load_w <= 0 else available_kwh / (current_load_w / 1000)
    return {
        "estimated_runway_hours": None if hours is None else round(hours, 2),
        "assumptions": {
            "current_load_w": current_load_w,
            "usable_capacity_kwh": usable_capacity_kwh,
            "minimum_soc_pct": min_soc_pct,
            "load_assumed_constant": True,
        },
    }
