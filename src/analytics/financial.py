def financial_metrics(
    grid_import_avoided_kwh: float,
    tariff_per_kwh: float,
    capex: float,
    maintenance_cost: float = 0.0,
    period_days: float | None = None,
) -> dict:
    """Return transparent simple financial metrics for the configured period.

    Payback is only estimated when a positive observation period is supplied;
    savings are annualized from that period. This is a simple payback estimate,
    not a discounted-cash-flow or NPV calculation.
    """
    avoided_cost = grid_import_avoided_kwh * tariff_per_kwh
    net_savings = avoided_cost - maintenance_cost
    simple_roi_pct = 100 * net_savings / capex if capex else None

    annualized_net_savings = None
    simple_payback_years = None
    if period_days and period_days > 0:
        annualized_net_savings = net_savings * 365.0 / period_days
        if capex and annualized_net_savings > 0:
            simple_payback_years = capex / annualized_net_savings

    return {
        "avoided_energy_cost": round(avoided_cost, 2),
        "net_savings": round(net_savings, 2),
        "simple_roi_pct": None if simple_roi_pct is None else round(simple_roi_pct, 2),
        "annualized_net_savings": None if annualized_net_savings is None else round(annualized_net_savings, 2),
        "simple_payback_years": None if simple_payback_years is None else round(simple_payback_years, 2),
        "assumptions": {
            "tariff_per_kwh": tariff_per_kwh,
            "capex": capex,
            "maintenance_cost": maintenance_cost,
            "period_days": period_days,
            "payback_method": "annualized simple payback; no discount rate or financing effects",
        },
    }
