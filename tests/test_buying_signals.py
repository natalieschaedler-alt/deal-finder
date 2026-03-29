from logic.image_analysis import analyze_listing_images
from logic.vision_analysis import inspect_listing_images
from logic.opportunity import calculate_opportunity_score
from logic.budget_optimizer import optimize_deal_selection
from database.deal_actions import load_deal_actions, save_deal_action
from database.models import Deal, Product


def test_image_analysis_handles_missing_images():
    result = analyze_listing_images([])

    assert result["score"] is None
    assert result["inspected_count"] == 0
    assert "Keine Bilder" in result["summary"]


def test_image_analysis_handles_failed_download(monkeypatch):
    def fake_get(*args, **kwargs):
        raise RuntimeError("download failed")

    monkeypatch.setattr("logic.image_analysis.requests.get", fake_get)

    result = analyze_listing_images(["https://example.com/image.jpg"])

    assert result["score"] is None
    assert result["inspected_count"] == 0
    assert "nicht ausgewertet" in result["summary"]


def test_opportunity_score_rewards_low_price_and_margin():
    strong = calculate_opportunity_score(
        offer_price=300,
        product_max_price=450,
        net_profit=120,
        roi_percent=35,
        demand=1.2,
        risk_penalty=0,
        max_buy_price=390,
        image_score=8,
    )
    weak = calculate_opportunity_score(
        offer_price=430,
        product_max_price=450,
        net_profit=35,
        roi_percent=8,
        demand=0.9,
        risk_penalty=3,
        max_buy_price=435,
        image_score=4,
    )

    assert strong > weak
    assert strong > 55


def test_vision_analysis_uses_heuristic_without_api_key():
    result = inspect_listing_images(
        image_urls=[],
        title="iPhone 13",
        stated_condition="sehr gut",
    )

    assert result["source"] == "Keine Bilder"
    assert result["condition_assessment"] == "sehr gut"


def test_vision_analysis_parses_api_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"score": 8.4, "summary": "Display wirkt sauber", "damage_flags": ["leichte Kratzer"], "condition_assessment": "sehr gut"}'
                        }
                    }
                ]
            }

    monkeypatch.setattr("logic.vision_analysis.requests.post", lambda *args, **kwargs: FakeResponse())

    result = inspect_listing_images(
        image_urls=["https://example.com/1.jpg"],
        title="iPhone 13",
        stated_condition="gut",
        api_key="demo",
    )

    assert result["score"] == 8.4
    assert result["damage_flags"] == ["leichte Kratzer"]
    assert result["condition_assessment"] == "sehr gut"


def test_budget_optimizer_prefers_best_combination_under_budget():
    product = Product("iPhone 13", "Smartphone", "sehr gut", ["Kabel"], 300, 450, 50, 500)
    deal_a = Deal(product=product, deal_id="a", offer_title="A", offer_price=300, offer_url="a", location="B", condition="sehr gut", accessories=["Kabel"], resale_price=500, profit=100, recommendation="Deal", net_profit=95, roi_percent=31, opportunity_score=70, capital_efficiency=0.317)
    deal_b = Deal(product=product, deal_id="b", offer_title="B", offer_price=250, offer_url="b", location="B", condition="sehr gut", accessories=["Kabel"], resale_price=420, profit=80, recommendation="Deal", net_profit=78, roi_percent=31, opportunity_score=60, capital_efficiency=0.312)
    deal_c = Deal(product=product, deal_id="c", offer_title="C", offer_price=550, offer_url="c", location="B", condition="sehr gut", accessories=["Kabel"], resale_price=800, profit=150, recommendation="Deal", net_profit=145, roi_percent=26, opportunity_score=74, capital_efficiency=0.264)

    result = optimize_deal_selection([deal_a, deal_b, deal_c], budget=600, max_items=2)

    assert [deal.deal_id for deal in result["selected_deals"]] == ["a", "b"]
    assert result["total_spend"] == 550
    assert result["remaining_budget"] == 50


def test_save_and_load_deal_actions(tmp_path):
    filepath = tmp_path / "actions.json"

    save_deal_action("deal-1", "iPhone 13", "KAUFEN", "sofort", str(filepath))
    actions = load_deal_actions(str(filepath))

    assert len(actions) == 1
    assert actions[0]["deal_id"] == "deal-1"
    assert actions[0]["action"] == "KAUFEN"