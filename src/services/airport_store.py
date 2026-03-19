"""ChromaDB-backed semantic airport and city code lookup.

On first use the collection is populated from AIRPORT_DATA and persisted to
.chroma_db/ in the project root. Subsequent calls reuse the cached DB.

Semantic search means queries like "Big Apple", "City of Light", or even
misspellings will resolve to the correct IATA codes.
"""

import os
import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------------------------
# Airport data — each entry's 'doc' is the text that gets embedded.
# Pack it with every reasonable alias so semantic search finds it.
# ---------------------------------------------------------------------------
AIRPORT_DATA = [
    # USA
    {"iata": "JFK", "city_code": "NYC", "city": "New York", "country": "USA",
     "doc": "JFK John F Kennedy International Airport New York United States NYC new york city big apple manhattan brooklyn queens east coast"},
    {"iata": "LGA", "city_code": "NYC", "city": "New York", "country": "USA",
     "doc": "LGA LaGuardia Airport New York United States NYC new york city queens"},
    {"iata": "EWR", "city_code": "NYC", "city": "Newark", "country": "USA",
     "doc": "EWR Newark Liberty International Airport New York New Jersey United States NYC"},
    {"iata": "LAX", "city_code": "LAX", "city": "Los Angeles", "country": "USA",
     "doc": "LAX Los Angeles International Airport California United States LA hollywood city of angels west coast"},
    {"iata": "ORD", "city_code": "CHI", "city": "Chicago", "country": "USA",
     "doc": "ORD O'Hare International Airport Chicago Illinois United States CHI windy city chi-town"},
    {"iata": "MDW", "city_code": "CHI", "city": "Chicago", "country": "USA",
     "doc": "MDW Midway Airport Chicago Illinois United States CHI windy city"},
    {"iata": "SFO", "city_code": "SFO", "city": "San Francisco", "country": "USA",
     "doc": "SFO San Francisco International Airport California United States SF bay area silicon valley golden gate"},
    {"iata": "MIA", "city_code": "MIA", "city": "Miami", "country": "USA",
     "doc": "MIA Miami International Airport Florida United States magic city south beach"},
    {"iata": "BOS", "city_code": "BOS", "city": "Boston", "country": "USA",
     "doc": "BOS Logan International Airport Boston Massachusetts United States beantown"},
    {"iata": "SEA", "city_code": "SEA", "city": "Seattle", "country": "USA",
     "doc": "SEA Seattle-Tacoma International Airport Washington United States SEA-TAC emerald city pacific northwest"},
    {"iata": "DCA", "city_code": "WAS", "city": "Washington DC", "country": "USA",
     "doc": "DCA Ronald Reagan Washington National Airport DC Washington United States capital city"},
    {"iata": "IAD", "city_code": "WAS", "city": "Washington DC", "country": "USA",
     "doc": "IAD Dulles International Airport Washington DC Virginia United States capital"},
    {"iata": "ATL", "city_code": "ATL", "city": "Atlanta", "country": "USA",
     "doc": "ATL Hartsfield-Jackson Atlanta International Airport Georgia United States"},
    {"iata": "DFW", "city_code": "DFW", "city": "Dallas", "country": "USA",
     "doc": "DFW Dallas Fort Worth International Airport Texas United States big D"},
    {"iata": "DEN", "city_code": "DEN", "city": "Denver", "country": "USA",
     "doc": "DEN Denver International Airport Colorado United States mile high city rocky mountains"},
    {"iata": "LAS", "city_code": "LAS", "city": "Las Vegas", "country": "USA",
     "doc": "LAS Harry Reid International Airport Las Vegas Nevada United States sin city the strip gambling"},
    {"iata": "MCO", "city_code": "ORL", "city": "Orlando", "country": "USA",
     "doc": "MCO Orlando International Airport Florida United States disney world theme parks"},
    {"iata": "IAH", "city_code": "HOU", "city": "Houston", "country": "USA",
     "doc": "IAH George Bush Intercontinental Airport Houston Texas United States space city"},
    {"iata": "PHX", "city_code": "PHX", "city": "Phoenix", "country": "USA",
     "doc": "PHX Phoenix Sky Harbor International Airport Arizona United States desert"},
    {"iata": "MSP", "city_code": "MSP", "city": "Minneapolis", "country": "USA",
     "doc": "MSP Minneapolis-Saint Paul International Airport Minnesota United States twin cities"},
    {"iata": "DTW", "city_code": "DTW", "city": "Detroit", "country": "USA",
     "doc": "DTW Detroit Metropolitan Airport Michigan United States motor city"},
    {"iata": "PHL", "city_code": "PHL", "city": "Philadelphia", "country": "USA",
     "doc": "PHL Philadelphia International Airport Pennsylvania United States philly city of brotherly love"},
    {"iata": "CLT", "city_code": "CLT", "city": "Charlotte", "country": "USA",
     "doc": "CLT Charlotte Douglas International Airport North Carolina United States"},
    {"iata": "SAN", "city_code": "SAN", "city": "San Diego", "country": "USA",
     "doc": "SAN San Diego International Airport California United States"},
    {"iata": "PDX", "city_code": "PDX", "city": "Portland", "country": "USA",
     "doc": "PDX Portland International Airport Oregon United States"},
    {"iata": "MSY", "city_code": "MSY", "city": "New Orleans", "country": "USA",
     "doc": "MSY Louis Armstrong New Orleans International Airport Louisiana United States NOLA big easy mardi gras jazz"},
    {"iata": "SLC", "city_code": "SLC", "city": "Salt Lake City", "country": "USA",
     "doc": "SLC Salt Lake City International Airport Utah United States"},
    {"iata": "AUS", "city_code": "AUS", "city": "Austin", "country": "USA",
     "doc": "AUS Austin-Bergstrom International Airport Texas United States live music capital"},
    {"iata": "BNA", "city_code": "BNA", "city": "Nashville", "country": "USA",
     "doc": "BNA Nashville International Airport Tennessee United States music city country music"},

    # Europe
    {"iata": "LHR", "city_code": "LON", "city": "London", "country": "UK",
     "doc": "LHR Heathrow Airport London United Kingdom UK england big smoke capital"},
    {"iata": "LGW", "city_code": "LON", "city": "London", "country": "UK",
     "doc": "LGW Gatwick Airport London United Kingdom UK england"},
    {"iata": "STN", "city_code": "LON", "city": "London", "country": "UK",
     "doc": "STN Stansted Airport London United Kingdom UK england"},
    {"iata": "CDG", "city_code": "PAR", "city": "Paris", "country": "France",
     "doc": "CDG Charles de Gaulle Airport Paris France city of light city of love ville lumiere eiffel tower"},
    {"iata": "ORY", "city_code": "PAR", "city": "Paris", "country": "France",
     "doc": "ORY Orly Airport Paris France city of light"},
    {"iata": "FCO", "city_code": "ROM", "city": "Rome", "country": "Italy",
     "doc": "FCO Leonardo da Vinci Fiumicino Airport Rome Italy eternal city roma italia"},
    {"iata": "AMS", "city_code": "AMS", "city": "Amsterdam", "country": "Netherlands",
     "doc": "AMS Amsterdam Schiphol Airport Netherlands Holland dutch venice of the north"},
    {"iata": "FRA", "city_code": "FRA", "city": "Frankfurt", "country": "Germany",
     "doc": "FRA Frankfurt Airport Germany deutsche banking city"},
    {"iata": "MAD", "city_code": "MAD", "city": "Madrid", "country": "Spain",
     "doc": "MAD Adolfo Suarez Madrid-Barajas Airport Spain espana capital"},
    {"iata": "BCN", "city_code": "BCN", "city": "Barcelona", "country": "Spain",
     "doc": "BCN Josep Tarradellas Barcelona-El Prat Airport Spain Catalunya Gaudi"},
    {"iata": "BER", "city_code": "BER", "city": "Berlin", "country": "Germany",
     "doc": "BER Berlin Brandenburg Airport Germany capital"},
    {"iata": "MUC", "city_code": "MUC", "city": "Munich", "country": "Germany",
     "doc": "MUC Munich Airport Bavaria Germany oktoberfest beer"},
    {"iata": "ZRH", "city_code": "ZRH", "city": "Zurich", "country": "Switzerland",
     "doc": "ZRH Zurich Airport Switzerland swiss banking finance"},
    {"iata": "VIE", "city_code": "VIE", "city": "Vienna", "country": "Austria",
     "doc": "VIE Vienna International Airport Austria wien classical music"},
    {"iata": "DUB", "city_code": "DUB", "city": "Dublin", "country": "Ireland",
     "doc": "DUB Dublin Airport Ireland emerald isle gaelic"},
    {"iata": "LIS", "city_code": "LIS", "city": "Lisbon", "country": "Portugal",
     "doc": "LIS Humberto Delgado Airport Lisbon Portugal lisboa city of seven hills"},
    {"iata": "BRU", "city_code": "BRU", "city": "Brussels", "country": "Belgium",
     "doc": "BRU Brussels Airport Belgium EU capital europe headquarters"},
    {"iata": "MXP", "city_code": "MIL", "city": "Milan", "country": "Italy",
     "doc": "MXP Milan Malpensa Airport Italy fashion capital lombardy"},
    {"iata": "LIN", "city_code": "MIL", "city": "Milan", "country": "Italy",
     "doc": "LIN Milan Linate Airport Italy fashion design"},
    {"iata": "ATH", "city_code": "ATH", "city": "Athens", "country": "Greece",
     "doc": "ATH Athens Eleftherios Venizelos Airport Greece hellenic acropolis parthenon"},
    {"iata": "PRG", "city_code": "PRG", "city": "Prague", "country": "Czech Republic",
     "doc": "PRG Vaclav Havel Airport Prague Czech Republic bohemia golden city"},
    {"iata": "CPH", "city_code": "CPH", "city": "Copenhagen", "country": "Denmark",
     "doc": "CPH Copenhagen Airport Denmark danish scandinavia nordic"},
    {"iata": "ARN", "city_code": "STO", "city": "Stockholm", "country": "Sweden",
     "doc": "ARN Stockholm Arlanda Airport Sweden swedish scandinavia nordic venice of the north"},
    {"iata": "OSL", "city_code": "OSL", "city": "Oslo", "country": "Norway",
     "doc": "OSL Oslo Airport Norway norwegian scandinavia nordic fjords"},
    {"iata": "HEL", "city_code": "HEL", "city": "Helsinki", "country": "Finland",
     "doc": "HEL Helsinki-Vantaa Airport Finland finnish nordic scandinavia"},
    {"iata": "WAW", "city_code": "WAW", "city": "Warsaw", "country": "Poland",
     "doc": "WAW Warsaw Chopin Airport Poland polska capital"},
    {"iata": "BUD", "city_code": "BUD", "city": "Budapest", "country": "Hungary",
     "doc": "BUD Budapest Liszt Ferenc Airport Hungary pearl of the danube"},
    {"iata": "OTP", "city_code": "BUH", "city": "Bucharest", "country": "Romania",
     "doc": "OTP Henri Coanda International Airport Bucharest Romania"},
    {"iata": "IST", "city_code": "IST", "city": "Istanbul", "country": "Turkey",
     "doc": "IST Istanbul Airport Turkey turkish bosphorus bridge east west"},
    {"iata": "SVQ", "city_code": "SVQ", "city": "Seville", "country": "Spain",
     "doc": "SVQ Seville Airport Spain andalusia flamenco"},
    {"iata": "NCE", "city_code": "NCE", "city": "Nice", "country": "France",
     "doc": "NCE Nice Côte d'Azur Airport France french riviera cote d azur"},
    {"iata": "MRS", "city_code": "MRS", "city": "Marseille", "country": "France",
     "doc": "MRS Marseille Provence Airport France"},
    {"iata": "GVA", "city_code": "GVA", "city": "Geneva", "country": "Switzerland",
     "doc": "GVA Geneva Airport Switzerland UN headquarters lake leman"},

    # Asia
    {"iata": "NRT", "city_code": "TYO", "city": "Tokyo", "country": "Japan",
     "doc": "NRT Narita International Airport Tokyo Japan rising sun land of the rising sun japanese"},
    {"iata": "HND", "city_code": "TYO", "city": "Tokyo", "country": "Japan",
     "doc": "HND Haneda Airport Tokyo Japan japanese capital"},
    {"iata": "KIX", "city_code": "OSA", "city": "Osaka", "country": "Japan",
     "doc": "KIX Kansai International Airport Osaka Japan"},
    {"iata": "PEK", "city_code": "BJS", "city": "Beijing", "country": "China",
     "doc": "PEK Beijing Capital International Airport China chinese capital forbidden city"},
    {"iata": "PKX", "city_code": "BJS", "city": "Beijing", "country": "China",
     "doc": "PKX Beijing Daxing International Airport China chinese capital"},
    {"iata": "PVG", "city_code": "SHA", "city": "Shanghai", "country": "China",
     "doc": "PVG Shanghai Pudong International Airport China financial hub bund"},
    {"iata": "HKG", "city_code": "HKG", "city": "Hong Kong", "country": "Hong Kong",
     "doc": "HKG Hong Kong International Airport fragrant harbour pearl of the orient"},
    {"iata": "SIN", "city_code": "SIN", "city": "Singapore", "country": "Singapore",
     "doc": "SIN Changi Airport Singapore lion city garden city southeast asia"},
    {"iata": "BKK", "city_code": "BKK", "city": "Bangkok", "country": "Thailand",
     "doc": "BKK Suvarnabhumi Airport Bangkok Thailand thai city of angels"},
    {"iata": "ICN", "city_code": "SEL", "city": "Seoul", "country": "South Korea",
     "doc": "ICN Incheon International Airport Seoul South Korea korean capital"},
    {"iata": "TPE", "city_code": "TPE", "city": "Taipei", "country": "Taiwan",
     "doc": "TPE Taiwan Taoyuan International Airport Taipei Taiwan"},
    {"iata": "DXB", "city_code": "DXB", "city": "Dubai", "country": "UAE",
     "doc": "DXB Dubai International Airport United Arab Emirates UAE gulf city of gold"},
    {"iata": "AUH", "city_code": "AUH", "city": "Abu Dhabi", "country": "UAE",
     "doc": "AUH Abu Dhabi International Airport UAE United Arab Emirates gulf"},
    {"iata": "BOM", "city_code": "BOM", "city": "Mumbai", "country": "India",
     "doc": "BOM Chhatrapati Shivaji Maharaj International Airport Mumbai India bombay bollywood financial capital"},
    {"iata": "DEL", "city_code": "DEL", "city": "Delhi", "country": "India",
     "doc": "DEL Indira Gandhi International Airport Delhi India new delhi capital"},
    {"iata": "SYD", "city_code": "SYD", "city": "Sydney", "country": "Australia",
     "doc": "SYD Sydney Kingsford Smith Airport Australia harbour city opera house"},
    {"iata": "MEL", "city_code": "MEL", "city": "Melbourne", "country": "Australia",
     "doc": "MEL Melbourne Airport Australia cultural capital"},
    {"iata": "AKL", "city_code": "AKL", "city": "Auckland", "country": "New Zealand",
     "doc": "AKL Auckland International Airport New Zealand city of sails kiwi"},
    {"iata": "KUL", "city_code": "KUL", "city": "Kuala Lumpur", "country": "Malaysia",
     "doc": "KUL Kuala Lumpur International Airport Malaysia KLIA petronas towers"},
    {"iata": "CGK", "city_code": "JKT", "city": "Jakarta", "country": "Indonesia",
     "doc": "CGK Soekarno-Hatta International Airport Jakarta Indonesia"},
    {"iata": "MNL", "city_code": "MNL", "city": "Manila", "country": "Philippines",
     "doc": "MNL Ninoy Aquino International Airport Manila Philippines pearl of the orient"},
    {"iata": "DOH", "city_code": "DOH", "city": "Doha", "country": "Qatar",
     "doc": "DOH Hamad International Airport Doha Qatar gulf peninsula"},
    {"iata": "TLV", "city_code": "TLV", "city": "Tel Aviv", "country": "Israel",
     "doc": "TLV Ben Gurion International Airport Tel Aviv Israel holy land"},
    {"iata": "BEY", "city_code": "BEY", "city": "Beirut", "country": "Lebanon",
     "doc": "BEY Rafic Hariri International Airport Beirut Lebanon paris of the middle east"},

    # Americas
    {"iata": "YYZ", "city_code": "YTO", "city": "Toronto", "country": "Canada",
     "doc": "YYZ Toronto Pearson International Airport Canada ontario toronto the good"},
    {"iata": "YVR", "city_code": "YVR", "city": "Vancouver", "country": "Canada",
     "doc": "YVR Vancouver International Airport Canada british columbia pacific coast"},
    {"iata": "YUL", "city_code": "YMQ", "city": "Montreal", "country": "Canada",
     "doc": "YUL Montreal-Trudeau International Airport Quebec Canada french canadian"},
    {"iata": "YOW", "city_code": "YOW", "city": "Ottawa", "country": "Canada",
     "doc": "YOW Ottawa International Airport Canada capital"},
    {"iata": "MEX", "city_code": "MEX", "city": "Mexico City", "country": "Mexico",
     "doc": "MEX Mexico City International Airport Mexico CDMX capital aztec"},
    {"iata": "CUN", "city_code": "CUN", "city": "Cancun", "country": "Mexico",
     "doc": "CUN Cancun International Airport Mexico resort beach caribbean riviera maya"},
    {"iata": "GRU", "city_code": "SAO", "city": "São Paulo", "country": "Brazil",
     "doc": "GRU Guarulhos International Airport Sao Paulo Brazil south america financial hub"},
    {"iata": "GIG", "city_code": "RIO", "city": "Rio de Janeiro", "country": "Brazil",
     "doc": "GIG Rio de Janeiro Galeao International Airport Brazil carnival christ the redeemer copacabana"},
    {"iata": "EZE", "city_code": "BUE", "city": "Buenos Aires", "country": "Argentina",
     "doc": "EZE Ministro Pistarini Airport Buenos Aires Argentina paris of the south tango"},
    {"iata": "LIM", "city_code": "LIM", "city": "Lima", "country": "Peru",
     "doc": "LIM Jorge Chavez International Airport Lima Peru south america"},
    {"iata": "BOG", "city_code": "BOG", "city": "Bogotá", "country": "Colombia",
     "doc": "BOG El Dorado International Airport Bogota Colombia south america"},
    {"iata": "SCL", "city_code": "SCL", "city": "Santiago", "country": "Chile",
     "doc": "SCL Arturo Merino Benitez International Airport Santiago Chile south america"},
    {"iata": "MDE", "city_code": "MDE", "city": "Medellín", "country": "Colombia",
     "doc": "MDE Jose Maria Cordova International Airport Medellin Colombia eternal spring city"},

    # Middle East & Africa
    {"iata": "CAI", "city_code": "CAI", "city": "Cairo", "country": "Egypt",
     "doc": "CAI Cairo International Airport Egypt north africa pyramids giza sphinx nile"},
    {"iata": "JNB", "city_code": "JNB", "city": "Johannesburg", "country": "South Africa",
     "doc": "JNB OR Tambo International Airport Johannesburg South Africa joburg egoli"},
    {"iata": "CPT", "city_code": "CPT", "city": "Cape Town", "country": "South Africa",
     "doc": "CPT Cape Town International Airport South Africa mother city table mountain"},
    {"iata": "NBO", "city_code": "NBO", "city": "Nairobi", "country": "Kenya",
     "doc": "NBO Jomo Kenyatta International Airport Nairobi Kenya east africa safari"},
    {"iata": "ADD", "city_code": "ADD", "city": "Addis Ababa", "country": "Ethiopia",
     "doc": "ADD Bole International Airport Addis Ababa Ethiopia africa hub"},
    {"iata": "LOS", "city_code": "LOS", "city": "Lagos", "country": "Nigeria",
     "doc": "LOS Murtala Muhammed International Airport Lagos Nigeria west africa"},
    {"iata": "CMN", "city_code": "CAS", "city": "Casablanca", "country": "Morocco",
     "doc": "CMN Mohammed V International Airport Casablanca Morocco north africa"},
    {"iata": "RUH", "city_code": "RUH", "city": "Riyadh", "country": "Saudi Arabia",
     "doc": "RUH King Khalid International Airport Riyadh Saudi Arabia middle east gulf"},
    {"iata": "JED", "city_code": "JED", "city": "Jeddah", "country": "Saudi Arabia",
     "doc": "JED King Abdulaziz International Airport Jeddah Saudi Arabia red sea mecca"},
    {"iata": "KWI", "city_code": "KWI", "city": "Kuwait City", "country": "Kuwait",
     "doc": "KWI Kuwait International Airport Kuwait City gulf middle east"},
    {"iata": "MCT", "city_code": "MCT", "city": "Muscat", "country": "Oman",
     "doc": "MCT Muscat International Airport Oman arabian peninsula gulf"},

    # Leisure / Popular Destinations
    {"iata": "HNL", "city_code": "HNL", "city": "Honolulu", "country": "USA",
     "doc": "HNL Daniel K Inouye International Airport Honolulu Hawaii United States waikiki beach tropical paradise aloha"},
    {"iata": "NAS", "city_code": "NAS", "city": "Nassau", "country": "Bahamas",
     "doc": "NAS Lynden Pindling International Airport Nassau Bahamas caribbean beach tropical"},
    {"iata": "MBJ", "city_code": "MBJ", "city": "Montego Bay", "country": "Jamaica",
     "doc": "MBJ Sangster International Airport Montego Bay Jamaica caribbean reggae beach"},
    {"iata": "PUJ", "city_code": "PUJ", "city": "Punta Cana", "country": "Dominican Republic",
     "doc": "PUJ Punta Cana International Airport Dominican Republic caribbean resort beach"},
    {"iata": "AUA", "city_code": "AUA", "city": "Aruba", "country": "Aruba",
     "doc": "AUA Queen Beatrix International Airport Aruba caribbean island beach resort ABC islands"},
    {"iata": "SXM", "city_code": "SXM", "city": "Saint Martin", "country": "Saint Martin",
     "doc": "SXM Princess Juliana International Airport Saint Martin Sint Maarten caribbean island"},
    {"iata": "GCM", "city_code": "GCM", "city": "Grand Cayman", "country": "Cayman Islands",
     "doc": "GCM Owen Roberts International Airport Grand Cayman Cayman Islands caribbean beach diving"},
    {"iata": "HER", "city_code": "HER", "city": "Heraklion", "country": "Greece",
     "doc": "HER Heraklion International Airport Crete Greece mediterranean island"},
    {"iata": "RHO", "city_code": "RHO", "city": "Rhodes", "country": "Greece",
     "doc": "RHO Rhodes International Airport Rhodes Greece greek island mediterranean"},
    {"iata": "PMI", "city_code": "PMI", "city": "Palma de Mallorca", "country": "Spain",
     "doc": "PMI Palma de Mallorca Airport Spain balearic islands mediterranean resort"},
    {"iata": "IBZ", "city_code": "IBZ", "city": "Ibiza", "country": "Spain",
     "doc": "IBZ Ibiza Airport Spain balearic islands nightlife beach"},
    {"iata": "DPS", "city_code": "DPS", "city": "Bali", "country": "Indonesia",
     "doc": "DPS Ngurah Rai International Airport Bali Indonesia island of the gods tropical paradise"},
    {"iata": "MLE", "city_code": "MLE", "city": "Malé", "country": "Maldives",
     "doc": "MLE Velana International Airport Male Maldives indian ocean island paradise overwater bungalow"},
    {"iata": "PPT", "city_code": "PPT", "city": "Papeete", "country": "French Polynesia",
     "doc": "PPT Faa'a International Airport Papeete Tahiti French Polynesia south pacific paradise bora bora"},
    {"iata": "NAN", "city_code": "NAN", "city": "Nadi", "country": "Fiji",
     "doc": "NAN Nadi International Airport Fiji south pacific island tropical"},
]

# ---------------------------------------------------------------------------
# Singleton store
# ---------------------------------------------------------------------------
_COLLECTION_NAME = "airports"
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".chroma_db")
_store = None


def _get_store():
    global _store
    if _store is not None:
        return _store

    db_path = os.path.abspath(_DB_PATH)
    client = chromadb.PersistentClient(path=db_path)

    # Use ChromaDB's built-in default embedding function
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Populate on first run (empty collection)
    if collection.count() == 0:
        collection.add(
            ids=[a["iata"] for a in AIRPORT_DATA],
            documents=[a["doc"] for a in AIRPORT_DATA],
            metadatas=[
                {
                    "iata": a["iata"],
                    "city_code": a["city_code"],
                    "city": a["city"],
                    "country": a["country"],
                }
                for a in AIRPORT_DATA
            ],
        )

    _store = collection
    return _store


def find_airport(query: str) -> dict | None:
    """Return the best matching airport metadata or None if no good match.

    Returns dict with keys: iata, city_code, city, country.
    """
    # Fast-path: exact IATA match (3-letter uppercase)
    q = query.strip().upper()
    if len(q) == 3 and q.isalpha():
        for a in AIRPORT_DATA:
            if a["iata"] == q:
                return {"iata": a["iata"], "city_code": a["city_code"],
                        "city": a["city"], "country": a["country"]}

    results = _get_store().query(
        query_texts=[query],
        n_results=1,
        include=["metadatas", "distances"],
    )

    if not results["metadatas"] or not results["metadatas"][0]:
        return None

    # Cosine distance — lower is better; reject weak matches
    distance = results["distances"][0][0]
    if distance > 0.7:
        return None

    return results["metadatas"][0][0]


def find_city(query: str) -> dict | None:
    """Same as find_airport but intended for hotel city-code lookups."""
    return find_airport(query)
