"""Hotel tool definitions for Claude."""

from ..services.hotel_service import HotelService

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
                    "type": "integer",
                    "description": "Number of guests (default: 1)",
                    "default": 1
                },
                "rooms": {
                    "type": "integer",
                    "description": "Number of rooms needed (default: 1)",
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

# Common city codes mapping (for hotels, these differ slightly from airports)
CITY_CODES = {
    # USA
    "new york": "NYC",
    "nyc": "NYC",
    "los angeles": "LAX",
    "la": "LAX",
    "chicago": "CHI",
    "san francisco": "SFO",
    "miami": "MIA",
    "boston": "BOS",
    "seattle": "SEA",
    "washington": "WAS",
    "dc": "WAS",
    "atlanta": "ATL",
    "dallas": "DFW",
    "denver": "DEN",
    "las vegas": "LAS",
    "orlando": "ORL",
    "houston": "HOU",
    "phoenix": "PHX",
    
    # Europe
    "london": "LON",
    "paris": "PAR",
    "rome": "ROM",
    "amsterdam": "AMS",
    "frankfurt": "FRA",
    "madrid": "MAD",
    "barcelona": "BCN",
    "berlin": "BER",
    "munich": "MUC",
    "zurich": "ZRH",
    "vienna": "VIE",
    "dublin": "DUB",
    "lisbon": "LIS",
    "brussels": "BRU",
    "milan": "MIL",
    "athens": "ATH",
    "prague": "PRG",
    "copenhagen": "CPH",
    "stockholm": "STO",
    "oslo": "OSL",
    "helsinki": "HEL",
    
    # Asia
    "tokyo": "TYO",
    "osaka": "OSA",
    "beijing": "BJS",
    "shanghai": "SHA",
    "hong kong": "HKG",
    "singapore": "SIN",
    "bangkok": "BKK",
    "seoul": "SEL",
    "taipei": "TPE",
    "dubai": "DXB",
    "mumbai": "BOM",
    "delhi": "DEL",
    "sydney": "SYD",
    "melbourne": "MEL",
    "auckland": "AKL",
    
    # Americas
    "toronto": "YTO",
    "vancouver": "YVR",
    "montreal": "YMQ",
    "mexico city": "MEX",
    "cancun": "CUN",
    "sao paulo": "SAO",
    "rio de janeiro": "RIO",
    "buenos aires": "BUE",
    "lima": "LIM",
    "bogota": "BOG",
    
    # Middle East & Africa
    "tel aviv": "TLV",
    "istanbul": "IST",
    "cairo": "CAI",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "doha": "DOH",
    "abu dhabi": "AUH",
}

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
            guests=tool_input.get("guests", 1),
            rooms=tool_input.get("rooms", 1)
        )
        return result.format_display()
    
    elif tool_name == "get_city_code":
        city = tool_input["city_name"].lower().strip()
        
        # Direct lookup
        if city in CITY_CODES:
            code = CITY_CODES[city]
            return f"The IATA city code for {tool_input['city_name']} is {code}"
        
        # Partial match
        for key, code in CITY_CODES.items():
            if city in key or key in city:
                return f"The IATA city code for {tool_input['city_name']} is {code}"
        
        # Check if it's already a code
        if len(city) == 3 and city.isalpha():
            return f"{city.upper()} appears to already be an IATA city code"
        
        return f"Could not find city code for '{tool_input['city_name']}'. Please provide a valid city name or code."
    
    return f"Unknown hotel tool: {tool_name}"
