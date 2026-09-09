def sustainability_metrics(displaced_grid_kwh: float, emissions_factor_kg_per_kwh: float) -> dict:
    avoided = displaced_grid_kwh * emissions_factor_kg_per_kwh
    return {
        "estimated_avoided_emissions_kgco2e": round(avoided, 2),
        "assumptions": {
            "displaced_grid_kwh": displaced_grid_kwh,
            "grid_emissions_factor_kg_per_kwh": emissions_factor_kg_per_kwh,
            "counterfactual": "grid_displacement",
        },
    }
