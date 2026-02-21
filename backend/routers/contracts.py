"""
Contracts Router — Live MSME Opportunity Search
Searches 13 Indian portals (GeM, NSIC, CPPP, SIDBI, etc.) for live contracts.
"""
from fastapi import APIRouter, Query
from typing import Optional
from services.contract_search import search_contracts

router = APIRouter(prefix="/contracts", tags=["Contract Search"])


@router.get(
    "/search",
    summary="🔍 Search live MSME contracts & opportunities from 13 Indian portals",
)
async def search_msme_contracts(
    product_desc: str = Query(..., description="Product or service description, e.g. 'handmade leather shoes'"),
    location: Optional[str] = Query(None, description="City/district, e.g. 'Agra'"),
    state: Optional[str] = Query(None, description="State, e.g. 'Uttar Pradesh'"),
    top_k: int = Query(10, ge=1, le=20, description="Number of results to return"),
):
    """
    Fetches live tenders and business opportunities from:
    - GeM, NSIC, SIDBI, KVIC, ONDC, DC MSME, TradeIndia, IndiaMart,
      SC/ST Hub, ZED, TReDS, CPPP (live RSS), NIC Tenders (live RSS)

    Results are **ranked by relevance** to your product description + location.
    """
    return await search_contracts(
        product_desc=product_desc,
        location=location,
        state=state,
        top_k=top_k,
    )


@router.get("/portals", summary="List all searched MSME portals")
async def list_portals():
    """Returns the list of all portals searched in the contract search."""
    return {
        "portals": [
            {"name": "GeM", "url": "https://gems.gov.in", "type": "Government Procurement"},
            {"name": "NSIC", "url": "https://nsic.co.in", "type": "Tendering"},
            {"name": "SIDBI", "url": "https://sidbi.in", "type": "Finance"},
            {"name": "KVIC", "url": "https://kvic.gov.in", "type": "Subsidy"},
            {"name": "ONDC", "url": "https://ondc.org", "type": "E-Commerce"},
            {"name": "DC MSME", "url": "https://dcmsme.gov.in", "type": "Cluster Dev"},
            {"name": "TradeIndia", "url": "https://tradeindia.com", "type": "B2B Marketplace"},
            {"name": "IndiaMart", "url": "https://indiamart.com", "type": "B2B Marketplace"},
            {"name": "SC/ST Hub", "url": "https://scsthub.in", "type": "Reserved Procurement"},
            {"name": "ZED Portal", "url": "https://zed.msme.gov.in", "type": "Quality Certification"},
            {"name": "TReDS", "url": "https://rxil.in", "type": "Invoice Finance"},
            {"name": "CPPP", "url": "https://eprocure.gov.in", "type": "Live Tenders"},
            {"name": "NIC Tenders", "url": "https://tendersinfo.com", "type": "Live Tenders"},
        ],
        "total": 13,
    }
