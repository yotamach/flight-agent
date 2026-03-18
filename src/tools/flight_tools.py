"""Flight tool definitions for Claude."""

from ..services.flight_service import FlightService

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
                    "type": "integer",
                    "description": "Number of adult passengers (default: 1)",
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

# Common airport codes mapping
AIRPORT_CODES = {
    # USA
    "new york": "JFK",
    "nyc": "JFK",
    "los angeles": "LAX",
    "la": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO",
    "miami": "MIA",
    "boston": "BOS",
    "seattle": "SEA",
    "washington": "DCA",
    "dc": "DCA",
    "atlanta": "ATL",
    "dallas": "DFW",
    "denver": "DEN",
    "las vegas": "LAS",
    "orlando": "MCO",
    "houston": "IAH",
    "phoenix": "PHX",
    
    # Europe
    "london": "LHR",
    "paris": "CDG",
    "rome": "FCO",
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
    "milan": "MXP",
    "athens": "ATH",
    "prague": "PRG",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    
    # Asia
    "tokyo": "NRT",
    "osaka": "KIX",
    "beijing": "PEK",
    "shanghai": "PVG",
    "hong kong": "HKG",
    "singapore": "SIN",
    "bangkok": "BKK",
    "seoul": "ICN",
    "taipei": "TPE",
    "dubai": "DXB",
    "mumbai": "BOM",
    "delhi": "DEL",
    "sydney": "SYD",
    "melbourne": "MEL",
    "auckland": "AKL",
    
    # Americas
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "mexico city": "MEX",
    "cancun": "CUN",
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",
    "buenos aires": "EZE",
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
            passengers=tool_input.get("passengers", 1),
            cabin_class=tool_input.get("cabin_class", "ECONOMY")
        )
        return result.format_display()
    
    elif tool_name == "get_airport_code":
        city = tool_input["city_or_airport"].lower().strip()
        
        # Direct lookup
        if city in AIRPORT_CODES:
            code = AIRPORT_CODES[city]
            return f"The IATA airport code for {tool_input['city_or_airport']} is {code}"
        
        # Partial match
        for key, code in AIRPORT_CODES.items():
            if city in key or key in city:
                return f"The IATA airport code for {tool_input['city_or_airport']} is {code}"
        
        # Check if it's already a code
        if len(city) == 3 and city.isalpha():
            return f"{city.upper()} appears to already be an IATA airport code"
        
        return f"Could not find airport code for '{tool_input['city_or_airport']}'. Please provide a valid city name or airport code."
    
    return f"Unknown flight tool: {tool_name}"
