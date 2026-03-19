"""Utility tools: save_itinerary and calculate_budget."""

import os
import json
from datetime import datetime

UTILITY_TOOLS = [
    {
        "name": "save_itinerary",
        "description": (
            "Save the final trip itinerary to a file so the user can refer to it later. "
            "Call this when the user has confirmed their travel plans and wants to save them. "
            "Include all flights, hotels, dates, and a cost summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Main destination city, e.g. 'Paris'"
                },
                "travel_dates": {
                    "type": "string",
                    "description": "Travel date range, e.g. 'March 15-22, 2026'"
                },
                "flights": {
                    "type": "string",
                    "description": "Flight details summary"
                },
                "hotels": {
                    "type": "string",
                    "description": "Hotel details summary"
                },
                "total_cost": {
                    "type": "number",
                    "description": "Estimated total trip cost in USD"
                },
                "notes": {
                    "type": "string",
                    "description": "Any additional notes or recommendations"
                }
            },
            "required": ["destination", "travel_dates", "flights", "hotels"]
        }
    },
    {
        "name": "calculate_budget",
        "description": (
            "Calculate a full trip budget breakdown from flight cost, hotel cost, and daily expenses. "
            "Use this when the user asks for a cost estimate or budget summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "flight_cost": {
                    "type": "number",
                    "description": "Total flight cost in USD (all passengers)"
                },
                "hotel_cost": {
                    "type": "number",
                    "description": "Total hotel cost in USD (all nights)"
                },
                "nights": {
                    "anyOf": [{"type": "integer"}, {"type": "string"}],
                    "description": "Number of nights"
                },
                "travelers": {
                    "anyOf": [{"type": "integer"}, {"type": "string"}],
                    "description": "Number of travelers",
                    "default": 1
                },
                "daily_expenses_per_person": {
                    "type": "number",
                    "description": "Estimated daily spending per person in USD (meals, transport, activities). Default: 100",
                    "default": 100
                }
            },
            "required": ["flight_cost", "hotel_cost", "nights"]
        }
    }
]


def handle_utility_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "save_itinerary":
        return _save_itinerary(tool_input)
    if tool_name == "calculate_budget":
        return _calculate_budget(tool_input)
    return f"Unknown utility tool: {tool_name}"


def _save_itinerary(data: dict) -> str:
    os.makedirs("itineraries", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_dest = data["destination"].replace(" ", "_").replace("/", "-")
    filename = f"itineraries/trip_{safe_dest}_{timestamp}.json"

    itinerary = {
        "destination": data["destination"],
        "travel_dates": data["travel_dates"],
        "flights": data["flights"],
        "hotels": data["hotels"],
        "total_cost_usd": data.get("total_cost"),
        "notes": data.get("notes", ""),
        "saved_at": datetime.now().isoformat(),
    }

    with open(filename, "w") as f:
        json.dump(itinerary, f, indent=2)

    return f"Itinerary saved to {filename}"


def _calculate_budget(data: dict) -> str:
    flight = float(data["flight_cost"])
    hotel = float(data["hotel_cost"])
    nights = int(data["nights"])
    travelers = int(data.get("travelers", 1))
    daily = float(data.get("daily_expenses_per_person", 100))

    daily_total = daily * travelers * nights
    grand_total = flight + hotel + daily_total
    per_person = grand_total / travelers if travelers > 0 else grand_total

    lines = [
        "Trip Budget Breakdown",
        f"  Flights:         ${flight:,.2f}",
        f"  Hotels:          ${hotel:,.2f}",
        f"  Daily expenses:  ${daily_total:,.2f}  ({travelers} traveler(s) × {nights} nights × ${daily:.0f}/day)",
        f"  ─────────────────────────────",
        f"  Total:           ${grand_total:,.2f}",
        f"  Per person:      ${per_person:,.2f}",
    ]
    return "\n".join(lines)
