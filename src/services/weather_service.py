"""Weather service using wttr.in (no API key required)."""

import httpx


class WeatherService:
    BASE_URL = "https://wttr.in/{city}?format=j1"
    TIMEOUT = 10

    def get_weather(self, city: str) -> str:
        """Return a human-readable weather summary for the city (current + 3-day forecast)."""
        try:
            url = self.BASE_URL.format(city=city.replace(" ", "+"))
            response = httpx.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            return f"Could not fetch weather for '{city}': {e}"
        except Exception as e:
            return f"Weather service error: {e}"

        return self._format(city, data)

    def _format(self, city: str, data: dict) -> str:
        lines = [f"Weather for {city}"]

        # Current conditions
        cur = data.get("current_condition", [{}])[0]
        desc = cur.get("weatherDesc", [{}])[0].get("value", "N/A")
        temp_c = cur.get("temp_C", "N/A")
        temp_f = cur.get("temp_F", "N/A")
        humidity = cur.get("humidity", "N/A")
        wind_kmph = cur.get("windspeedKmph", "N/A")
        feels_c = cur.get("FeelsLikeC", "N/A")

        lines.append(
            f"Current: {desc}, {temp_c}°C / {temp_f}°F "
            f"(feels like {feels_c}°C), humidity {humidity}%, wind {wind_kmph} km/h"
        )

        # 3-day forecast
        for day in data.get("weather", []):
            date = day.get("date", "")
            max_c = day.get("maxtempC", "N/A")
            min_c = day.get("mintempC", "N/A")
            max_f = day.get("maxtempF", "N/A")
            min_f = day.get("mintempF", "N/A")
            # Pick midday description
            hourly = day.get("hourly", [])
            mid_desc = ""
            if hourly:
                mid = hourly[len(hourly) // 2]
                mid_desc = mid.get("weatherDesc", [{}])[0].get("value", "")
            lines.append(
                f"{date}: {mid_desc}, high {max_c}°C/{max_f}°F, low {min_c}°C/{min_f}°F"
            )

        lines.append("Note: forecast is current/near-term; long-range travel dates may differ.")
        return "\n".join(lines)
