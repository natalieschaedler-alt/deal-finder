from search.compliance import (
    build_compliant_offer,
    extract_city_region,
    infer_condition_and_accessories,
    is_public_listing_url,
    sanitize_text,
)


def test_sanitize_text_redacts_private_contact_data():
    text = "Kontakt: Max Mustermann, +49 170 1234567, max@example.com, Musterstraße 10"
    cleaned = sanitize_text(text)

    assert "@" not in cleaned
    assert "1234567" not in cleaned
    assert "Musterstraße" not in cleaned
    assert "[redacted-email]" in cleaned


def test_extract_city_region_keeps_only_city_level_location():
    assert extract_city_region("Berlin, Mitte, Prenzlauer Allee 21") == "Berlin, Mitte"
    assert extract_city_region("Hamburg") == "Hamburg"


def test_public_listing_url_blocks_login_and_captcha_paths():
    assert is_public_listing_url("https://www.ebay.de/itm/123")
    assert not is_public_listing_url("https://www.example.com/login?next=/itm/123")
    assert not is_public_listing_url("https://www.example.com/captcha")


def test_infer_condition_and_accessories_from_text():
    inferred = infer_condition_and_accessories(
        "iPhone 13 wie neu mit OVP und Ladekabel",
        fallback_condition="gut",
        expected_accessories=["OVP", "Ladekabel", "Huelle"],
    )

    assert inferred["condition"] == "wie neu"
    assert set(inferred["accessories"]) == {"OVP", "Ladekabel"}


def test_build_compliant_offer_returns_only_allowed_fields_and_sanitized_values():
    offer = build_compliant_offer(
        title="iPhone 13 von Max",
        price=399,
        description="Kontakt unter max@example.com oder +49 170 1234567",
        location="Berlin, Mitte, Musterstraße 10",
        link="https://www.ebay.de/itm/123",
        condition="gebraucht",
        accessories=["OVP"],
        source_platform="eBay",
        resale_price=520,
        seller_rating=95,
        listing_age_days=2,
        image_urls=[],
    )

    assert offer is not None
    assert set(offer.keys()) == {
        "offer_title",
        "offer_price",
        "offer_description",
        "offer_url",
        "location",
        "condition",
        "accessories",
        "source_platform",
        "resale_price",
        "seller_rating",
        "listing_age_days",
        "is_fake",
        "image_urls",
    }
    assert "@" not in offer["offer_description"]
    assert "1234567" not in offer["offer_description"]
