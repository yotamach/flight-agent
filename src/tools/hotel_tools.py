"""Hotel tool definitions for Claude."""

from ..services.hotel_service import HotelService
from ..services import airport_store

# Tool definitions for Claude
HOTEL_TOOLS = [
    {
        "name": "search_hotels",
        "description": "Search for available hotels in a city. Returns a list of hotel options with prices, ratings, and amenities. Use city IATA codes (e.g., PAR for Paris, LON for London, NYC for New York).",
        "input_schema": {
            "type": "object",
            "properties": {
                "city_code": {
                    "type": "string",
                    "description": "City IATA code (e.g., PAR, LON, NYC)"
                },
                "check_in": {
                    "type": "string",
                    "description": "Check-in date in YYYY-MM-DD format"
                },
                "check_out": {
                    "type": "string",
                    "description": "Check-out date in YYYY-MM-DD format"
                },
                "guests": {
                    "anyOf": [{"type": "integer"}, {"type": "string"}],
                    "description": "Number of guests as integer (default: 1)",
                    "default": 1
                },
                "rooms": {
                    "anyOf": [{"type": "integer"}, {"type": "string"}],
                    "description": "Number of rooms needed as integer (default: 1)",
                    "default": 1
                }
            },
            "required": ["city_code", "check_in", "check_out"]
        }
    },
    {
        "name": "get_city_code",
        "description": "Get the IATA city code for a city name. Use this when the user mentions a city name for hotel searches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "City name to look up"
                }
            },
            "required": ["city_name"]
        }
    }
]

# Initialize service
_hotel_service = HotelService()


def handle_hotel_tool(tool_name: str, tool_input: dict) -> str:
    """
    Handle hotel-related tool calls from Claude.
    
    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
        
    Returns:
        String result to return to Claude
    """
    if tool_name == "search_hotels":
        result = _hotel_service.search_hotels(
            city_code=tool_input["city_code"],
            check_in=tool_input["check_in"],
            check_out=tool_input["check_out"],
            guests=int(tool_input.get("guests", 1)),
            rooms=int(tool_input.get("rooms", 1))
        )
        return result.format_display()
    
    elif tool_name == "get_city_code":
        query = tool_input["city_name"]
        match = airport_store.find_city(query)
        if match:
            return (
                f"The IATA city code for {query} is {match['city_code']} "
                f"({match['city']}, {match['country']})"
            )
        return f"Could not find city code for '{query}'. Please provide a valid city name."
    
    return f"Unknown hotel tool: {tool_name}"
