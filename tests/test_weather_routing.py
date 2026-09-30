from angel_platform.webui.server import _extract_weather_location, asks_for_tomorrow_weather


def test_extracts_city_from_natural_tomorrow_phrase():
    assert _extract_weather_location("what is the weather forecast for Indianapolis for tomorrow") == "Indianapolis"


def test_extracts_city_from_standard_phrase():
    assert _extract_weather_location("weather in Indianapolis tomorrow") == "Indianapolis"


def test_does_not_consume_intent_word_as_location():
    assert _extract_weather_location("forecast for Beech Grove, Indiana tomorrow") == "Beech Grove, Indiana"


def test_tomorrow_weather_intent_is_detected():
    assert asks_for_tomorrow_weather("what is the weather forecast for Indianapolis for tomorrow")
