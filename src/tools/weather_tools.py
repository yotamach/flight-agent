"""Weather tool definition and handler."""

from ..services.weather_service import WeatherService

WEATHER_TOOLS = [
    {
        "name": "get_weather",
        "description": (
            "Get the current weather and 3-day forecast for a destination city. "
            "Use this to help travelers understand what conditions to expect. "
            "Call this after finding a destination, especially for beach, ski, or outdoor trips."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Paris', 'Tokyo', 'New York'"
                }
            },
            "required": ["city"]
        }
    }
]

_weather_service = WeatherService()


def handle_weather_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_weather":
        return _weather_service.get_weather(tool_input["city"])
    return f"Unknown weather tool: {tool_name}"
