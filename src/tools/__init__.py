"""Tool definitions for Claude agent."""

from .flight_tools import FLIGHT_TOOLS, handle_flight_tool
from .hotel_tools import HOTEL_TOOLS, handle_hotel_tool

# Combine all tools
ALL_TOOLS = FLIGHT_TOOLS + HOTEL_TOOLS

__all__ = [
    "FLIGHT_TOOLS",
    "HOTEL_TOOLS", 
    "ALL_TOOLS",
    "handle_flight_tool",
    "handle_hotel_tool"
]
