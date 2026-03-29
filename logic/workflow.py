from statistics import median


def run_search_workflow(
    config=None,
    show_console: bool = True,
    enable_notifications: bool = True,
    export_files: bool = True,
):
    from config.manager import ConfigManager
    from database.manager import ProductManager
    from database.models import Deal
    from search.manager import SearchManager
    from logic.demand import estimate_demand
    from logic.risk import estimate_risk
    from logic.advanced_evaluate import advanced_evaluate_deal
    from logic.product_discovery import discover_best_products
    from logic.market_pricing import build_trade_plan, normalize_condition
    from logic.opportunity import calculate_opportunity_score
    from logic.vision_analysis import inspect_listing_images
    from logic.budget_optimizer import optimize_deal_selection
    from logic.deal_identity import build_deal_id
    from dashboard.display import show_deals
    from dashboard.export import export_budget_plan_csv, export_deals_csv
    from dashboard.filters import sort_deals
    from utils.notify import send_email, send_telegram
    import logging

    config = config or ConfigManager()
    logger = logging.getLogger("deal_finder")
    product_manager = ProductManager()
    search_manager = SearchManager()

    fee_percent_config = float(config.get("marketplace_fee_percent", 10))
    fee_rate = fee_percent_config / 100 if fee_percent_config > 1 else fee_percent_config
    fixed_cost_per_sale = float(config.get("fixed_cost_per_sale", 5))
    min_net_profit = float(config.get("min_net_profit", 30))
    enable_image_analysis = bool(config.get("enable_image_analysis", True))
    enable_vision_analysis = bool(config.get("enable_vision_analysis", True))
    image_timeout_seconds = int(config.get("image_analysis_timeout_seconds", 5))
    image_max_images = int(config.get("image_analysis_max_images", 3))
    vision_timeout_seconds = int(config.get("vision_timeout_seconds", 15))
    vision_api_key = config.get("vision_api_key", "")
    vision_api_url = config.get("vision_api_url", "https://api.openai.com/v1/chat/completions")
    vision_model = config.get("vision_model", "gpt-4.1-mini")
    vision_provider_name = config.get("vision_provider_name", "OpenAI-kompatibel")
    max_purchase_budget = float(config.get("max_purchase_budget", 0))
    max_budget_items = int(config.get("max_budget_items", 0))

    if config.get("auto_discover_products", False):
        discovered = discover_best_products(search_manager, config)
        if discovered:
            product_manager.products = discovered
            logger.info("Auto-Discovery aktiv: %s Produkte ausgewahlt.", len(discovered))

    all_deals = []
    for product in product_manager.products:
        offers = search_manager.search_all(product)
        market_metrics = (
            search_manager.get_market_metrics(product)
            if hasattr(search_manager, "get_market_metrics")
            else {"sold_prices": [], "sold_by_condition": {}, "sold_history": []}
        )
        sold_prices_global = market_metrics.get("sold_prices", [])
        sold_by_condition = market_metrics.get("sold_by_condition", {})
        sold_history_global = market_metrics.get("sold_history", [])

        if not offers:
            offers = [
                {
                    "offer_title": f"{product.name} fast neu",
                    "offer_price": product.max_price - 20,
                    "offer_url": "https://beispiel.de/angebot1",
                    "image_urls": [],
                    "location": config.get("default_location", "Berlin"),
                    "condition": product.condition,
                    "accessories": product.accessories,
                    "resale_price": product.min_resale_price + 50,
                    "seller_rating": 5,
                    "is_fake": False,
                }
            ]

        for angebot in offers:
            demand = estimate_demand(product.name)
            risk_factors = estimate_risk(angebot)
            eval_result = advanced_evaluate_deal(
                product,
                angebot["offer_price"],
                angebot["resale_price"],
                angebot["condition"],
                angebot["accessories"],
                angebot["location"],
                demand,
                risk_factors,
            )
            cond_key = normalize_condition(angebot.get("condition", "")).lower()
            sold_prices_condition = sold_by_condition.get(cond_key, [])
            has_live_market_data = bool(sold_prices_condition or sold_prices_global)
            image_result = inspect_listing_images(
                image_urls=angebot.get("image_urls", []),
                title=angebot.get("offer_title", product.name),
                stated_condition=angebot.get("condition", product.condition),
                timeout_seconds=vision_timeout_seconds if enable_vision_analysis else image_timeout_seconds,
                max_images=image_max_images,
                api_key=vision_api_key if enable_vision_analysis else "",
                api_url=vision_api_url,
                model=vision_model,
                provider_name=vision_provider_name,
            ) if enable_image_analysis else {
                "score": None,
                "summary": "Bildanalyse deaktiviert",
                "inspected_count": 0,
                "source": "Deaktiviert",
                "damage_flags": [],
                "condition_assessment": angebot.get("condition", product.condition),
            }
            sold_history_condition = [
                history_item for history_item in sold_history_global
                if normalize_condition(history_item.get("condition", "")).lower() == cond_key
            ]
            effective_history = sold_history_condition or sold_history_global
            pricing = build_trade_plan(
                offer_price=angebot["offer_price"],
                sold_prices=sold_prices_condition or sold_prices_global,
                fee_rate=fee_rate,
                fixed_cost_per_sale=fixed_cost_per_sale,
                min_net_profit=min_net_profit,
                offer_condition=angebot.get("condition", product.condition),
                product_condition=product.condition,
                fallback_sell_price=angebot.get("resale_price", product.min_resale_price),
            )
            target_sell_price = pricing["target_sell_price"]
            net_profit = pricing["expected_net_profit"]
            roi_percent = pricing["roi_percent"]
            sold_price_values = [item.get("sold_price", 0) for item in effective_history if item.get("sold_price", 0) > 0]
            sold_price_median = round(float(median(sold_price_values)), 2) if sold_price_values else None
            sold_source_summary = "eBay" if effective_history else ""
            risk_penalty = sum(risk_factors.values()) if risk_factors else 0
            capital_efficiency = round((net_profit / angebot["offer_price"]), 3) if angebot["offer_price"] > 0 else 0
            opportunity_score = calculate_opportunity_score(
                offer_price=angebot["offer_price"],
                product_max_price=product.max_price,
                net_profit=net_profit,
                roi_percent=roi_percent,
                demand=demand,
                risk_penalty=risk_penalty,
                max_buy_price=pricing["max_buy_price"],
                image_score=image_result.get("score"),
            )
            buy_price_gap = round(pricing["max_buy_price"] - angebot["offer_price"], 2)
            vision_damage_flags = image_result.get("damage_flags", [])
            vision_summary = image_result.get("summary", "")
            if vision_damage_flags:
                vision_summary = f"{vision_summary} | Hinweise: {', '.join(vision_damage_flags)}"

            buy_decision = (
                "KAUFEN"
                if eval_result["recommendation"] == "Deal"
                and angebot["offer_price"] <= pricing["max_buy_price"]
                and net_profit >= min_net_profit
                and opportunity_score >= float(config.get("min_opportunity_score", 30))
                else "WARTEN"
            )
            deal = Deal(
                product=product,
                offer_title=angebot["offer_title"],
                offer_price=angebot["offer_price"],
                offer_url=angebot["offer_url"],
                location=angebot["location"],
                condition=angebot["condition"],
                accessories=angebot["accessories"],
                resale_price=target_sell_price,
                profit=eval_result["profit"],
                recommendation=eval_result["recommendation"],
                risk=", ".join(eval_result["reasons"]),
                target_sell_price=target_sell_price,
                max_buy_price=pricing["max_buy_price"],
                net_profit=net_profit,
                roi_percent=roi_percent,
                buy_decision=buy_decision,
                price_data_quality="Echt" if has_live_market_data else "Fallback",
                sold_count=len(effective_history),
                sold_price_median=sold_price_median,
                sold_source_summary=sold_source_summary,
                sold_history=effective_history[:8],
                image_score=image_result.get("score"),
                image_summary=image_result.get("summary", ""),
                vision_score=image_result.get("score"),
                vision_summary=vision_summary,
                vision_source=image_result.get("source", "Heuristik"),
                opportunity_score=opportunity_score,
                buy_price_gap=buy_price_gap,
                capital_efficiency=capital_efficiency,
                deal_id=build_deal_id(product.name, angebot["offer_title"], angebot["offer_url"]),
            )
            if deal.buy_decision == "KAUFEN":
                all_deals.append(deal)

    filtered = [deal for deal in all_deals if (deal.net_profit or 0) >= min_net_profit]
    sorted_deals = sort_deals(filtered, by="opportunity_score", reverse=True)
    budget_plan = optimize_deal_selection(sorted_deals, max_purchase_budget, max_items=max_budget_items)
    selected_deals = budget_plan["selected_deals"]

    if show_console:
        show_deals(sorted_deals)
    if export_files:
        export_deals_csv(sorted_deals)
        export_budget_plan_csv(selected_deals)
    if enable_notifications and sorted_deals:
        best_deal = selected_deals[0] if selected_deals else sorted_deals[0]
        deal_message = (
            f"{len(sorted_deals)} neue Deals. Bester Deal: {best_deal.product.name} | "
            f"Einkauf {best_deal.offer_price:.2f} EUR | "
            f"Verkauf {best_deal.target_sell_price:.2f} EUR | "
            f"Netto-Gewinn {best_deal.net_profit:.2f} EUR | "
            f"Verkaufe: {best_deal.sold_count}x ({best_deal.sold_source_summary or 'n/a'}) | "
            f"Chance {best_deal.opportunity_score:.1f} | "
            f"Budgetplan {len(selected_deals)} Deals / {budget_plan['total_spend']:.2f} EUR"
        )
        send_email("Neue Deals gefunden!", deal_message, config.get("notify_email", ""))
        send_telegram(deal_message, config.get("notify_telegram", ""))
    elif not sorted_deals:
        logger.info("Keine neuen Deals gefunden.")

    return {
        "deals": sorted_deals,
        "selected_deals": selected_deals,
        "budget_plan": budget_plan,
        "product_count": len(product_manager.products),
    }
