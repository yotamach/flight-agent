"""Flight data models."""

from pydantic import BaseModel
from datetime import datetime


class FlightSegment(BaseModel):
    """A single flight segment."""
    
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    carrier: str
    flight_number: str
    duration: str
    

class Flight(BaseModel):
    """A flight offer with one or more segments."""
    
    id: str
    segments: list[FlightSegment]
    price: float
    currency: str
    cabin_class: str = "ECONOMY"
    total_duration: str
    stops: int
    
    def format_display(self) -> str:
        """Format flight for display."""
        first_seg = self.segments[0]
        last_seg = self.segments[-1]
        
        stops_text = "Direct" if self.stops == 0 else f"{self.stops} stop(s)"
        
        return (
            f"✈️  {first_seg.carrier} {first_seg.flight_number}\n"
            f"   {first_seg.departure_airport} → {last_seg.arrival_airport}\n"
            f"   Depart: {first_seg.departure_time}\n"
            f"   Arrive: {last_seg.arrival_time}\n"
            f"   Duration: {self.total_duration} | {stops_text}\n"
            f"   💰 {self.currency} {self.price:.2f}"
        )


class FlightSearchResult(BaseModel):
    """Results from a flight search."""
    
    flights: list[Flight]
    origin: str
    destination: str
    departure_date: str
    return_date: str | None = None
    
    def format_display(self) -> str:
        """Format search results for display."""
        if not self.flights:
            return "No flights found for your search criteria."
        
        header = f"\n🔍 Found {len(self.flights)} flight(s) from {self.origin} to {self.destination}\n"
        header += f"   Date: {self.departure_date}"
        if self.return_date:
            header += f" - {self.return_date}"
        header += "\n" + "=" * 50 + "\n"
        
        flights_text = "\n\n".join(f.format_display() for f in self.flights[:5])
        
        return header + flights_text
