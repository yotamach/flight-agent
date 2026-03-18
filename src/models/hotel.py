"""Hotel data models."""

from pydantic import BaseModel


class Hotel(BaseModel):
    """A hotel offer."""
    
    id: str
    name: str
    city: str
    address: str | None = None
    rating: float | None = None
    price_per_night: float
    total_price: float
    currency: str
    amenities: list[str] = []
    room_type: str = "Standard Room"
    
    def format_display(self) -> str:
        """Format hotel for display."""
        rating_stars = "⭐" * int(self.rating) if self.rating else "No rating"
        
        amenities_text = ", ".join(self.amenities[:5]) if self.amenities else "Contact hotel for amenities"
        
        return (
            f"🏨 {self.name}\n"
            f"   {rating_stars}\n"
            f"   📍 {self.address or self.city}\n"
            f"   🛏️  {self.room_type}\n"
            f"   💰 {self.currency} {self.price_per_night:.2f}/night "
            f"(Total: {self.currency} {self.total_price:.2f})\n"
            f"   ✨ {amenities_text}"
        )


class HotelSearchResult(BaseModel):
    """Results from a hotel search."""
    
    hotels: list[Hotel]
    city: str
    check_in: str
    check_out: str
    guests: int = 1
    
    def format_display(self) -> str:
        """Format search results for display."""
        if not self.hotels:
            return "No hotels found for your search criteria."
        
        header = f"\n🔍 Found {len(self.hotels)} hotel(s) in {self.city}\n"
        header += f"   Check-in: {self.check_in} | Check-out: {self.check_out}\n"
        header += "=" * 50 + "\n"
        
        hotels_text = "\n\n".join(h.format_display() for h in self.hotels[:5])
        
        return header + hotels_text
