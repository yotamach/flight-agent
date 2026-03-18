"""Flight service using Amadeus API."""

from amadeus import Client, ResponseError
from ..config import config
from ..models.flight import Flight, FlightSegment, FlightSearchResult


class FlightService:
    """Service for searching and retrieving flight information."""
    
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
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        passengers: int = 1,
        cabin_class: str = "ECONOMY"
    ) -> FlightSearchResult:
        """
        Search for available flights.
        
        Args:
            origin: Origin airport IATA code (e.g., 'JFK')
            destination: Destination airport IATA code (e.g., 'CDG')
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional)
            passengers: Number of adult passengers
            cabin_class: Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
            
        Returns:
            FlightSearchResult with available flights
        """
        if not self.client:
            return self._get_mock_flights(origin, destination, departure_date, return_date)
        
        try:
            search_params = {
                "originLocationCode": origin.upper(),
                "destinationLocationCode": destination.upper(),
                "departureDate": departure_date,
                "adults": passengers,
                "travelClass": cabin_class,
                "max": 10
            }
            
            if return_date:
                search_params["returnDate"] = return_date
            
            response = self.client.shopping.flight_offers_search.get(**search_params)
            
            flights = self._parse_flight_offers(response.data)
            
            return FlightSearchResult(
                flights=flights,
                origin=origin.upper(),
                destination=destination.upper(),
                departure_date=departure_date,
                return_date=return_date
            )
            
        except ResponseError as e:
            print(f"Amadeus API error: {e}")
            return self._get_mock_flights(origin, destination, departure_date, return_date)
    
    def _parse_flight_offers(self, offers: list) -> list[Flight]:
        """Parse Amadeus flight offers into Flight models."""
        flights = []
        
        for offer in offers:
            try:
                segments = []
                total_duration = ""
                
                for itinerary in offer.get("itineraries", []):
                    total_duration = itinerary.get("duration", "").replace("PT", "")
                    
                    for segment in itinerary.get("segments", []):
                        segments.append(FlightSegment(
                            departure_airport=segment["departure"]["iataCode"],
                            arrival_airport=segment["arrival"]["iataCode"],
                            departure_time=segment["departure"]["at"],
                            arrival_time=segment["arrival"]["at"],
                            carrier=segment.get("carrierCode", ""),
                            flight_number=segment.get("number", ""),
                            duration=segment.get("duration", "").replace("PT", "")
                        ))
                
                price_info = offer.get("price", {})
                
                flights.append(Flight(
                    id=offer.get("id", ""),
                    segments=segments,
                    price=float(price_info.get("total", 0)),
                    currency=price_info.get("currency", "USD"),
                    total_duration=total_duration,
                    stops=len(segments) - 1
                ))
                
            except (KeyError, ValueError) as e:
                print(f"Error parsing flight offer: {e}")
                continue
        
        return flights
    
    def _get_mock_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None
    ) -> FlightSearchResult:
        """Return mock flight data for testing without API keys."""
        mock_flights = [
            Flight(
                id="mock-1",
                segments=[
                    FlightSegment(
                        departure_airport=origin.upper(),
                        arrival_airport=destination.upper(),
                        departure_time=f"{departure_date}T08:00:00",
                        arrival_time=f"{departure_date}T14:30:00",
                        carrier="AA",
                        flight_number="100",
                        duration="6H30M"
                    )
                ],
                price=450.00,
                currency="USD",
                total_duration="6H30M",
                stops=0
            ),
            Flight(
                id="mock-2",
                segments=[
                    FlightSegment(
                        departure_airport=origin.upper(),
                        arrival_airport="LHR",
                        departure_time=f"{departure_date}T10:00:00",
                        arrival_time=f"{departure_date}T16:00:00",
                        carrier="BA",
                        flight_number="178",
                        duration="6H"
                    ),
                    FlightSegment(
                        departure_airport="LHR",
                        arrival_airport=destination.upper(),
                        departure_time=f"{departure_date}T18:00:00",
                        arrival_time=f"{departure_date}T20:30:00",
                        carrier="BA",
                        flight_number="324",
                        duration="2H30M"
                    )
                ],
                price=380.00,
                currency="USD",
                total_duration="10H30M",
                stops=1
            ),
            Flight(
                id="mock-3",
                segments=[
                    FlightSegment(
                        departure_airport=origin.upper(),
                        arrival_airport=destination.upper(),
                        departure_time=f"{departure_date}T19:00:00",
                        arrival_time=f"{departure_date}T23:45:00",
                        carrier="DL",
                        flight_number="240",
                        duration="7H45M"
                    )
                ],
                price=520.00,
                currency="USD",
                total_duration="7H45M",
                stops=0
            )
        ]
        
        return FlightSearchResult(
            flights=mock_flights,
            origin=origin.upper(),
            destination=destination.upper(),
            departure_date=departure_date,
            return_date=return_date
        )
