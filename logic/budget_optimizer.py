from typing import Dict, List

from database.models import Deal


def _deal_value(deal: Deal) -> float:
    net_profit = deal.net_profit or 0
    opportunity = deal.opportunity_score or 0
    efficiency = deal.capital_efficiency or 0
    return round((net_profit * 1.0) + (opportunity * 0.6) + (efficiency * 20), 2)


def optimize_deal_selection(deals: List[Deal], budget: float, max_items: int = 0) -> Dict[str, object]:
    if budget <= 0 or not deals:
        return {
            "selected_deals": deals,
            "total_spend": round(sum(deal.offer_price for deal in deals), 2),
            "total_net_profit": round(sum((deal.net_profit or 0) for deal in deals), 2),
            "remaining_budget": max(round(budget - sum(deal.offer_price for deal in deals), 2), 0),
        }

    candidates = [deal for deal in deals if deal.offer_price <= budget]
    states = {(0.0, 0): []}

    for deal in candidates:
        new_states = dict(states)
        for (spent, count), chosen in states.items():
            new_spent = round(spent + deal.offer_price, 2)
            new_count = count + 1
            if new_spent > budget:
                continue
            if max_items and new_count > max_items:
                continue

            proposal = chosen + [deal]
            state_key = (new_spent, new_count)
            if state_key not in new_states or _deal_value_sum(proposal) > _deal_value_sum(new_states[state_key]):
                new_states[state_key] = proposal
        states = new_states

    best_selection = []
    best_score = -1.0
    best_spend = 0.0
    for (spent, _count), chosen in states.items():
        score = _deal_value_sum(chosen)
        if score > best_score or (score == best_score and spent < best_spend):
            best_selection = chosen
            best_score = score
            best_spend = spent

    prioritized = sorted(best_selection, key=lambda deal: ((deal.opportunity_score or 0), (deal.net_profit or 0)), reverse=True)
    for index, deal in enumerate(prioritized, start=1):
        deal.budget_priority = index
        deal.recommended_purchase = True

    total_spend = round(sum(deal.offer_price for deal in prioritized), 2)
    total_net_profit = round(sum((deal.net_profit or 0) for deal in prioritized), 2)
    return {
        "selected_deals": prioritized,
        "total_spend": total_spend,
        "total_net_profit": total_net_profit,
        "remaining_budget": round(max(budget - total_spend, 0), 2),
    }


def _deal_value_sum(deals: List[Deal]) -> float:
    return round(sum(_deal_value(deal) for deal in deals), 2)