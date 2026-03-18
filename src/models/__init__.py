"""Data models for the Flight Agent."""

from .flight import Flight, FlightSearchResult
from .hotel import Hotel, HotelSearchResult

__all__ = ["Flight", "FlightSearchResult", "Hotel", "HotelSearchResult"]
