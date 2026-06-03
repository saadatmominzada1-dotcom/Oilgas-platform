"""
RSS Feed Sources for Oil & Gas News Platform
Organized by region and type
"""

RSS_FEEDS = [
    # ── WIRE SERVICES ───────────────────────────────────────────────────────
    {
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "name": "Reuters Business",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://rss.app/feeds/tXH0DsGDmJfMgpgQ.xml",
        "name": "Reuters Energy",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
        "name": "MarketWatch",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 8,
        "language": "en"
    },
    # ── ENERGY SPECIFIC ─────────────────────────────────────────────────────
    {
        "url": "https://oilprice.com/rss/main",
        "name": "OilPrice.com",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.rigzone.com/news/rss/rigzone_latest.aspx",
        "name": "Rigzone",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://www.offshore-technology.com/feed/",
        "name": "Offshore Technology",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.worldoil.com/rss-feeds/all-news",
        "name": "World Oil",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.naturalgasintel.com/feed/",
        "name": "Natural Gas Intelligence",
        "source_type": "Analysis",
        "region": "North America",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://energymonitor.ai/feed",
        "name": "Energy Monitor",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.energyintel.com/rss",
        "name": "Energy Intelligence",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://www.spglobal.com/commodityinsights/en/rss-feed/oil",
        "name": "S&P Global Commodity Insights",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 9,
        "language": "en"
    },
    # ── GOVERNMENT & REGULATORY ─────────────────────────────────────────────
    {
        "url": "https://www.eia.gov/rss/todayinenergy.xml",
        "name": "EIA Today in Energy",
        "source_type": "Government",
        "region": "North America",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.eia.gov/rss/news.xml",
        "name": "EIA News",
        "source_type": "Government",
        "region": "North America",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.iea.org/rssfeed/news/",
        "name": "IEA News",
        "source_type": "Government",
        "region": "Global",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.opec.org/opec_web/en/press_room/rss.htm",
        "name": "OPEC Press Room",
        "source_type": "Government",
        "region": "Middle East",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.neb-one.gc.ca/rss/nws/index-eng.xml",
        "name": "Canada Energy Regulator",
        "source_type": "Government",
        "region": "North America",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.npd.no/en/rss/news/",
        "name": "Norwegian Petroleum Directorate",
        "source_type": "Government",
        "region": "Europe",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.nstauthority.co.uk/news-publications/news/rss/",
        "name": "North Sea Transition Authority",
        "source_type": "Government",
        "region": "Europe",
        "credibility": 10,
        "language": "en"
    },
    {
        "url": "https://www.anp.gov.br/rss.xml",
        "name": "ANP Brazil",
        "source_type": "Government",
        "region": "Latin America",
        "credibility": 9,
        "language": "pt"
    },
    # ── MIDDLE EAST ─────────────────────────────────────────────────────────
    {
        "url": "https://www.arabianbusiness.com/rss",
        "name": "Arabian Business",
        "source_type": "Wire Service",
        "region": "Middle East",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.thenationalnews.com/rss/energy.xml",
        "name": "The National UAE - Energy",
        "source_type": "Wire Service",
        "region": "Middle East",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://www.mees.com/feed",
        "name": "MEES - Middle East Economic Survey",
        "source_type": "Analysis",
        "region": "Middle East",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://shana.ir/en/rss",
        "name": "SHANA - Iran Oil Ministry",
        "source_type": "Government",
        "region": "Middle East",
        "credibility": 8,
        "language": "en"
    },
    # ── AFRICA ──────────────────────────────────────────────────────────────
    {
        "url": "https://www.africaoilgasreport.com/feed/",
        "name": "Africa Oil & Gas Report",
        "source_type": "Analysis",
        "region": "Africa",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://energycapitalpower.com/feed/",
        "name": "Energy Capital & Power",
        "source_type": "Analysis",
        "region": "Africa",
        "credibility": 7,
        "language": "en"
    },
    # ── ASIA PACIFIC ────────────────────────────────────────────────────────
    {
        "url": "https://www.platts.com/rss/oilFeed",
        "name": "Platts Oil",
        "source_type": "Wire Service",
        "region": "Asia-Pacific",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://asia.nikkei.com/rss/feed/section/Business",
        "name": "Nikkei Asia Business",
        "source_type": "Wire Service",
        "region": "Asia-Pacific",
        "credibility": 8,
        "language": "en"
    },
    # ── EUROPE ──────────────────────────────────────────────────────────────
    {
        "url": "https://www.euractiv.com/section/energy/feed/",
        "name": "Euractiv Energy",
        "source_type": "Analysis",
        "region": "Europe",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://www.reuters.com/business/energy/rss",
        "name": "Reuters Energy Direct",
        "source_type": "Wire Service",
        "region": "Europe",
        "credibility": 10,
        "language": "en"
    },
    # ── RUSSIA / FSU ────────────────────────────────────────────────────────
    {
        "url": "https://tass.com/rss/v2.xml",
        "name": "TASS",
        "source_type": "Wire Service",
        "region": "Russia/FSU",
        "credibility": 6,
        "language": "en"
    },
    # ── NORTH AMERICA ───────────────────────────────────────────────────────
    {
        "url": "https://www.houstonchronicle.com/business/energy/rss",
        "name": "Houston Chronicle Energy",
        "source_type": "Wire Service",
        "region": "North America",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://www.ogj.com/rss/home.rss",
        "name": "Oil & Gas Journal",
        "source_type": "Analysis",
        "region": "North America",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://www.desmog.com/feed/",
        "name": "DeSmog",
        "source_type": "Analysis",
        "region": "North America",
        "credibility": 6,
        "language": "en"
    },
    # ── LATIN AMERICA ───────────────────────────────────────────────────────
    {
        "url": "https://www.bnamericas.com/rss/en/oil-gas.rss",
        "name": "BNAmericas Oil & Gas",
        "source_type": "Analysis",
        "region": "Latin America",
        "credibility": 7,
        "language": "en"
    },
    # ── POLITICAL / GEOPOLITICAL ────────────────────────────────────────────
    {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "name": "Al Jazeera",
        "source_type": "Wire Service",
        "region": "Middle East",
        "credibility": 7,
        "language": "en"
    },
    {
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "name": "BBC World News",
        "source_type": "Wire Service",
        "region": "Global",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://rss.dw.com/rss/en-bus",
        "name": "Deutsche Welle Business",
        "source_type": "Wire Service",
        "region": "Europe",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://www.france24.com/en/rss",
        "name": "France 24",
        "source_type": "Wire Service",
        "region": "Europe",
        "credibility": 8,
        "language": "en"
    },
    {
        "url": "https://foreignpolicy.com/feed/",
        "name": "Foreign Policy",
        "source_type": "Analysis",
        "region": "Global",
        "credibility": 9,
        "language": "en"
    },
    {
        "url": "https://www.middleeasteye.net/rss",
        "name": "Middle East Eye",
        "source_type": "Analysis",
        "region": "Middle East",
        "credibility": 7,
        "language": "en"
    },
]

# Keywords for oil/gas relevance scoring
OIL_GAS_KEYWORDS = {
    "tier1": [
        "oil", "crude", "petroleum", "brent", "wti", "opec", "barrel", "refinery",
        "lng", "natural gas", "pipeline", "upstream", "downstream", "drilling",
        "wellhead", "offshore", "onshore", "petrochemical", "gasoline", "diesel",
        "kerosene", "naphtha", "condensate", "fracking", "shale", "oilfield",
        "production cut", "output cut", "aramco", "adnoc", "bp", "shell", "exxon",
        "chevron", "total", "equinor", "eni", "petrobras", "rosneft", "gazprom",
        "energy minister", "oil minister", "hydrocarbon", "exploration", "reserves"
    ],
    "tier2": [
        "energy", "fuel", "commodity", "tanker", "supertanker", "vlcc", "cargo",
        "sanctions", "hormuz", "strait", "bab-el-mandeb", "suez", "bosphorus",
        "strategic reserve", "spr", "refining", "crack spread", "futures",
        "petrodollar", "energy security", "supply chain", "opec+", "non-opec",
        "carbon", "emission", "renewable", "transition", "iea", "eia", "noc",
        "national oil company", "concession", "production sharing", "royalty"
    ],
    "tier3_political": [
        "iran", "iraq", "saudi", "uae", "kuwait", "qatar", "libya", "nigeria",
        "venezuela", "russia", "kazakhstan", "azerbaijan", "norway", "canada",
        "mexico", "brazil", "angola", "algeria", "election", "coup", "sanctions",
        "embargo", "geopolit", "conflict", "war", "houthi", "militia", "drone attack"
    ]
}

# Major oil chokepoints and geopolitical triggers - auto-elevate to alert
GEOPOLITICAL_TRIGGERS = [
    "strait of hormuz", "bab-el-mandeb", "suez canal", "bosphorus", "malacca",
    "houthi", "drone attack on oil", "pipeline attack", "refinery attack",
    "opec+ meeting", "opec meeting", "emergency meeting", "production cut",
    "strategic petroleum reserve", "spr release", "force majeure",
    "nord stream", "turkstream", "keystone", "east-med",
]

# Country to region mapping
COUNTRY_REGION_MAP = {
    "Saudi Arabia": "Middle East", "UAE": "Middle East", "Iraq": "Middle East",
    "Iran": "Middle East", "Kuwait": "Middle East", "Qatar": "Middle East",
    "Oman": "Middle East", "Bahrain": "Middle East", "Yemen": "Middle East",
    "Libya": "Africa", "Nigeria": "Africa", "Angola": "Africa",
    "Algeria": "Africa", "Egypt": "Africa", "Equatorial Guinea": "Africa",
    "Gabon": "Africa", "Congo": "Africa",
    "Russia": "Russia/FSU", "Kazakhstan": "Russia/FSU", "Azerbaijan": "Russia/FSU",
    "Turkmenistan": "Russia/FSU", "Uzbekistan": "Russia/FSU",
    "USA": "North America", "United States": "North America", "Canada": "North America",
    "Mexico": "North America",
    "Norway": "Europe", "UK": "Europe", "United Kingdom": "Europe",
    "Netherlands": "Europe", "Germany": "Europe", "Italy": "Europe",
    "Brazil": "Latin America", "Venezuela": "Latin America",
    "Colombia": "Latin America", "Ecuador": "Latin America", "Peru": "Latin America",
    "China": "Asia-Pacific", "India": "Asia-Pacific", "Japan": "Asia-Pacific",
    "South Korea": "Asia-Pacific", "Australia": "Asia-Pacific",
    "Indonesia": "Asia-Pacific", "Malaysia": "Asia-Pacific",
}
