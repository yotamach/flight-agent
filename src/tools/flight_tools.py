"""Flight tool definitions for Claude."""

from ..services.flight_service import FlightService
from ..services import airport_store

# Tool definitions for Claude
FLIGHT_TOOLS = [
    {
        "name": "search_flights",
        "description": "Search for available flights between two airports. Returns a list of flight options with prices, times, and stops. Use airport IATA codes (e.g., JFK for New York JFK, CDG for Paris Charles de Gaulle, LHR for London Heathrow).",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Origin airport IATA code (e.g., JFK, LAX, ORD)"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport IATA code (e.g., CDG, LHR, NRT)"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format"
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date in YYYY-MM-DD format (optional, omit for one-way)"
                },
                "passengers": {
                    "anyOf": [{"type": "integer"}, {"type": "string"}],
                    "description": "Number of adult passengers as integer (default: 1)",
                    "default": 1
                },
                "cabin_class": {
                    "type": "string",
                    "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
                    "description": "Cabin class preference (default: ECONOMY)",
                    "default": "ECONOMY"
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    },
    {
        "name": "get_airport_code",
        "description": "Get the IATA airport code for a city or airport name. Use this when the user mentions a city name instead of an airport code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city_or_airport": {
                    "type": "string",
                    "description": "City name or airport name to look up"
                }
            },
            "required": ["city_or_airport"]
        }
    }
]

# Initialize service
_flight_service = FlightService()


def handle_flight_tool(tool_name: str, tool_input: dict) -> str:
    """
    Handle flight-related tool calls from Claude.
    
    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
        
    Returns:
        String result to return to Claude
    """
    if tool_name == "search_flights":
        result = _flight_service.search_flights(
            origin=tool_input["origin"],
            destination=tool_input["destination"],
            departure_date=tool_input["departure_date"],
            return_date=tool_input.get("return_date"),
            passengers=int(tool_input.get("passengers", 1)),
            cabin_class=tool_input.get("cabin_class", "ECONOMY")
        )
        return result.format_display()
    
    elif tool_name == "get_airport_code":
        query = tool_input["city_or_airport"]
        match = airport_store.find_airport(query)
        if match:
            return (
                f"The IATA airport code for {query} is {match['iata']} "
                f"({match['city']}, {match['country']})"
            )
        return f"Could not find airport code for '{query}'. Please provide a valid city or airport name."
    
    return f"Unknown flight tool: {tool_name}"
