"""Tests for the agent tools."""

import pytest
from src.tools.flight_tools import handle_flight_tool, AIRPORT_CODES
from src.tools.hotel_tools import handle_hotel_tool, CITY_CODES


class TestFlightTools:
    """Tests for flight tools."""
    
    def test_get_airport_code_known_city(self):
        """Test getting airport code for a known city."""
        result = handle_flight_tool("get_airport_code", {"city_or_airport": "New York"})
        assert "JFK" in result
    
    def test_get_airport_code_lowercase(self):
        """Test getting airport code with lowercase input."""
        result = handle_flight_tool("get_airport_code", {"city_or_airport": "paris"})
        assert "CDG" in result
    
    def test_get_airport_code_unknown_city(self):
        """Test getting airport code for an unknown city."""
        result = handle_flight_tool("get_airport_code", {"city_or_airport": "Unknown City XYZ"})
        assert "Could not find" in result
    
    def test_get_airport_code_already_code(self):
        """Test when input is already an airport code."""
        result = handle_flight_tool("get_airport_code", {"city_or_airport": "JFK"})
        assert "already" in result.lower() or "JFK" in result
    
    def test_search_flights_mock(self):
        """Test searching flights returns mock data."""
        result = handle_flight_tool("search_flights", {
            "origin": "JFK",
            "destination": "CDG",
            "departure_date": "2026-03-15"
        })
        assert "JFK" in result
        assert "CDG" in result
        assert "flight" in result.lower()


class TestHotelTools:
    """Tests for hotel tools."""
    
    def test_get_city_code_known_city(self):
        """Test getting city code for a known city."""
        result = handle_hotel_tool("get_city_code", {"city_name": "Paris"})
        assert "PAR" in result
    
    def test_get_city_code_lowercase(self):
        """Test getting city code with lowercase input."""
        result = handle_hotel_tool("get_city_code", {"city_name": "london"})
        assert "LON" in result
    
    def test_get_city_code_unknown_city(self):
        """Test getting city code for an unknown city."""
        result = handle_hotel_tool("get_city_code", {"city_name": "Unknown City XYZ"})
        assert "Could not find" in result
    
    def test_search_hotels_mock(self):
        """Test searching hotels returns mock data."""
        result = handle_hotel_tool("search_hotels", {
            "city_code": "PAR",
            "check_in": "2026-03-15",
            "check_out": "2026-03-20"
        })
        assert "PAR" in result
        assert "hotel" in result.lower()


class TestAirportCodesCoverage:
    """Test airport codes dictionary has good coverage."""
    
    def test_major_us_cities(self):
        """Test major US cities are covered."""
        us_cities = ["new york", "los angeles", "chicago", "miami", "boston"]
        for city in us_cities:
            assert city in AIRPORT_CODES, f"{city} should be in AIRPORT_CODES"
    
    def test_major_european_cities(self):
        """Test major European cities are covered."""
        eu_cities = ["london", "paris", "rome", "amsterdam", "berlin"]
        for city in eu_cities:
            assert city in AIRPORT_CODES, f"{city} should be in AIRPORT_CODES"
    
    def test_major_asian_cities(self):
        """Test major Asian cities are covered."""
        asian_cities = ["tokyo", "singapore", "hong kong", "bangkok", "dubai"]
        for city in asian_cities:
            assert city in AIRPORT_CODES, f"{city} should be in AIRPORT_CODES"


class TestCityCodesCoverage:
    """Test city codes dictionary has good coverage."""
    
    def test_major_tourist_destinations(self):
        """Test major tourist destinations are covered."""
        destinations = ["paris", "london", "tokyo", "rome", "barcelona", "dubai"]
        for city in destinations:
            assert city in CITY_CODES, f"{city} should be in CITY_CODES"
