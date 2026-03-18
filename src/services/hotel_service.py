"""Hotel service using Amadeus API."""

from amadeus import Client, ResponseError
from ..config import config
from ..models.hotel import Hotel, HotelSearchResult


class HotelService:
    """Service for searching and retrieving hotel information."""
    
    def __init__(self):
        """Initialize the Amadeus client."""
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the Amadeus client with credentials."""
        if config.AMADEUS_CLIENT_ID and config.AMADEUS_CLIENT_SECRET:
            self.client = Client(
                client_id=config.AMADEUS_CLIENT_ID,
                client_secret=config.AMADEUS_CLIENT_SECRET,
                hostname=config.AMADEUS_HOSTNAME
            )
    
    def search_hotels(
        self,
        city_code: str,
        check_in: str,
        check_out: str,
        guests: int = 1,
        rooms: int = 1
    ) -> HotelSearchResult:
        """
        Search for available hotels in a city.
        
        Args:
            city_code: City IATA code (e.g., 'PAR' for Paris)
            check_in: Check-in date in YYYY-MM-DD format
            check_out: Check-out date in YYYY-MM-DD format
            guests: Number of guests
            rooms: Number of rooms
            
        Returns:
            HotelSearchResult with available hotels
        """
        if not self.client:
            return self._get_mock_hotels(city_code, check_in, check_out, guests)
        
        try:
            # First, get hotel list for the city
            hotel_list = self.client.reference_data.locations.hotels.by_city.get(
                cityCode=city_code.upper()
            )
            
            if not hotel_list.data:
                return self._get_mock_hotels(city_code, check_in, check_out, guests)
            
            # Get hotel IDs (limit to first 20)
            hotel_ids = [h["hotelId"] for h in hotel_list.data[:20]]
            
            # Search for offers
            response = self.client.shopping.hotel_offers_search.get(
                hotelIds=hotel_ids,
                checkInDate=check_in,
                checkOutDate=check_out,
                adults=guests,
                roomQuantity=rooms
            )
            
            hotels = self._parse_hotel_offers(response.data, check_in, check_out)
            
            return HotelSearchResult(
                hotels=hotels,
                city=city_code.upper(),
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )
            
        except ResponseError as e:
            print(f"Amadeus API error: {e}")
            return self._get_mock_hotels(city_code, check_in, check_out, guests)
    
    def _parse_hotel_offers(self, offers: list, check_in: str, check_out: str) -> list[Hotel]:
        """Parse Amadeus hotel offers into Hotel models."""
        hotels = []
        
        # Calculate number of nights
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        for offer in offers:
            try:
                hotel_info = offer.get("hotel", {})
                hotel_offers = offer.get("offers", [])
                
                if not hotel_offers:
                    continue
                
                best_offer = hotel_offers[0]
                price_info = best_offer.get("price", {})
                total_price = float(price_info.get("total", 0))
                
                hotels.append(Hotel(
                    id=hotel_info.get("hotelId", ""),
                    name=hotel_info.get("name", "Unknown Hotel"),
                    city=hotel_info.get("cityCode", ""),
                    address=hotel_info.get("address", {}).get("lines", [""])[0] if hotel_info.get("address") else None,
                    rating=float(hotel_info.get("rating", 0)) if hotel_info.get("rating") else None,
                    price_per_night=total_price / nights if nights > 0 else total_price,
                    total_price=total_price,
                    currency=price_info.get("currency", "USD"),
                    room_type=best_offer.get("room", {}).get("description", {}).get("text", "Standard Room"),
                    amenities=hotel_info.get("amenities", [])[:5]
                ))
                
            except (KeyError, ValueError) as e:
                print(f"Error parsing hotel offer: {e}")
                continue
        
        return hotels
    
    def _get_mock_hotels(
        self,
        city_code: str,
        check_in: str,
        check_out: str,
        guests: int
    ) -> HotelSearchResult:
        """Return mock hotel data for testing without API keys."""
        
        # Calculate nights for mock data
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        mock_hotels = [
            Hotel(
                id="mock-hotel-1",
                name=f"Grand Hotel {city_code.upper()}",
                city=city_code.upper(),
                address="123 Main Street, City Center",
                rating=4.5,
                price_per_night=150.00,
                total_price=150.00 * nights,
                currency="USD",
                amenities=["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
                room_type="Deluxe Double Room"
            ),
            Hotel(
                id="mock-hotel-2",
                name=f"Budget Inn {city_code.upper()}",
                city=city_code.upper(),
                address="456 Side Street",
                rating=3.0,
                price_per_night=75.00,
                total_price=75.00 * nights,
                currency="USD",
                amenities=["WiFi", "Parking"],
                room_type="Standard Room"
            ),
            Hotel(
                id="mock-hotel-3",
                name=f"Luxury Resort {city_code.upper()}",
                city=city_code.upper(),
                address="789 Beach Boulevard",
                rating=5.0,
                price_per_night=350.00,
                total_price=350.00 * nights,
                currency="USD",
                amenities=["WiFi", "Pool", "Spa", "Restaurant", "Gym", "Beach Access"],
                room_type="Premium Suite"
            ),
            Hotel(
                id="mock-hotel-4",
                name=f"City Center Hotel {city_code.upper()}",
                city=city_code.upper(),
                address="101 Downtown Avenue",
                rating=4.0,
                price_per_night=120.00,
                total_price=120.00 * nights,
                currency="USD",
                amenities=["WiFi", "Restaurant", "Business Center"],
                room_type="Superior Room"
            )
        ]
        
        return HotelSearchResult(
            hotels=mock_hotels,
            city=city_code.upper(),
            check_in=check_in,
            check_out=check_out,
            guests=guests
        )
