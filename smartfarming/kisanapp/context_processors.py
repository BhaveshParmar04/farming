import requests
from django.core.cache import cache
from .models import FarmerRegistration


def weather_context(request):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return {"weather": None}

    cache_key = f"weather_openmeteo_{farmer_id}"
    cached = cache.get(cache_key)
    if cached:
        return {"weather": cached}

    try:
        farmer = FarmerRegistration.objects.get(id=farmer_id)
    except FarmerRegistration.DoesNotExist:
        return {"weather": None}

    city = farmer.district or farmer.village or farmer.state
    if not city:
        return {"weather": None}

    data = fetch_weather(city)
    if data:
        cache.set(cache_key, data, 60 * 30)  # 30 min cache

    return {"weather": data}


def fetch_weather(city):
    """Fetch weather using Open-Meteo (free, no API key needed)."""
    try:
        # Step 1: Geocoding
        geo_res = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10
        )
        geo_data = geo_res.json()
        if not geo_data.get("results"):
            return _demo_weather(city)

        place = geo_data["results"][0]
        lat   = place["latitude"]
        lon   = place["longitude"]
        name  = place["name"]

        # Step 2: Current weather + daily forecast
        weather_res = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":  lat,
                "longitude": lon,
                "current":   "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily":     "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone":  "Asia/Kolkata",
                "forecast_days": 3,
            },
            timeout=10
        )
        data    = weather_res.json()
        current = data.get("current", {})
        daily   = data.get("daily", {})

        temp     = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind     = current.get("wind_speed_10m")
        wcode    = current.get("weather_code", 0)

        # WMO weather code → condition + icon
        def wmo_to_info(code):
            if code == 0:                    return "Clear",          "☀️"
            if code in [1, 2]:               return "Partly Cloudy", "⛅"
            if code == 3:                    return "Overcast",       "☁️"
            if code in [45, 48]:             return "Fog",            "🌫️"
            if code in [51, 53, 55]:         return "Drizzle",        "🌦️"
            if code in [61, 63, 65]:         return "Rain",           "🌧️"
            if code in [71, 73, 75]:         return "Snow",           "❄️"
            if code in [80, 81, 82]:         return "Rain Showers",   "🌧️"
            if code in [95, 96, 99]:         return "Thunderstorm",   "⛈️"
            return "Cloudy", "🌤️"

        condition, icon = wmo_to_info(wcode)

        # Today + Tomorrow rain check
        rain_today    = False
        rain_tomorrow = False
        precip = daily.get("precipitation_sum", [])
        today_code    = (daily.get("weather_code") or [0])[0]
        tomorrow_code = (daily.get("weather_code") or [0, 0])[1] if len(daily.get("weather_code", [])) > 1 else 0

        if len(precip) > 0 and precip[0] and precip[0] > 1.0:
            rain_today = True
        if len(precip) > 1 and precip[1] and precip[1] > 1.0:
            rain_tomorrow = True

        # Forecast line — farming relevant
        def rain_chance(code):
            return code in [51,53,55,61,63,65,71,73,75,80,81,82,95,96,99]

        if rain_today and rain_tomorrow:
            forecast_line = "🌧️ Rain today & tomorrow — delay field work, check drainage."
        elif rain_today:
            forecast_line = "🌧️ Rain today — avoid spraying, good for irrigation."
        elif rain_tomorrow:
            forecast_line = "🌦️ Rain expected tomorrow — complete field work today."
        elif rain_chance(tomorrow_code):
            forecast_line = "⛅ Possible rain tomorrow — keep an eye on forecast."
        else:
            forecast_line = "☀️ Clear next 2 days — good for field work & spraying."

        alert = None
        alert_type = None
        if rain_today:
            alert = "🌧️ Rain today — avoid spraying, good for irrigation."
            alert_type = "rain"
        elif rain_tomorrow:
            alert = "🌦️ Rain expected tomorrow — complete field work today."
            alert_type = "rain"
        elif condition == "Thunderstorm":
            alert = "⛈️ Thunderstorm alert! Avoid field work today."
            alert_type = "storm"
        elif temp and temp > 40:
            alert = f"🌡️ Extreme heat ({temp}°C). Water crops early morning."
            alert_type = "heat"
        elif temp and temp < 10:
            alert = f"🥶 Cold wave ({temp}°C). Protect sensitive crops."
            alert_type = "cold"

        return {
            "city":          name,
            "location":      city,
            "temp":          round(temp) if temp is not None else "--",
            "feels":         round(temp) if temp is not None else "--",
            "humidity":      humidity or "--",
            "wind":          round(wind) if wind is not None else "--",
            "condition":     condition,
            "desc":          condition,
            "icon":          icon,
            "rain_today":    rain_today,
            "rain_tomorrow": rain_tomorrow,
            "forecast_line": forecast_line,
            "alert":         alert,
            "alert_type":    alert_type,
            "is_demo":       False,
        }

    except Exception as e:
        print("Weather Error:", e)
        return _demo_weather(city)


def _demo_weather(city):
    return {
        "city":         city,
        "location":     city,
        "temp":         28,
        "feels":        31,
        "humidity":     65,
        "wind":         12,
        "condition":    "Partly Cloudy",
        "desc":         "Partly Cloudy",
        "icon":         "⛅",
        "rain_tomorrow": True,
        "alert":        "🌧️ Rain likely tomorrow — plan irrigation accordingly.",
        "alert_type":   "rain",
        "is_demo":      True,
    }
