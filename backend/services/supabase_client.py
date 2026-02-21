"""
Supabase Client Service
Handles all database operations using Supabase REST API.
Table: mse_profiles
"""
import os
import httpx
from datetime import datetime
from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jdrhlpqggucpxvuikvwr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

REST_URL = f"{SUPABASE_URL}/rest/v1"

def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


async def insert_mse(data: dict) -> Optional[dict]:
    """Insert a new MSE profile into Supabase. Returns the inserted record."""
    payload = {
        "business_name":      data.get("business_name"),
        "owner_name":         data.get("owner_name"),
        "phone":              data.get("phone"),
        "location":           data.get("location"),
        "state":              data.get("state"),
        "product_description":data.get("product_description"),
        "ondc_category":      data.get("ondc_category"),
        "ondc_subcategory":   data.get("ondc_subcategory"),
        "hsn_code":           data.get("hsn_code"),
        "annual_capacity":    data.get("annual_capacity"),
        "preferred_language": data.get("preferred_language", "en"),
        "udyam_number":       data.get("udyam_number"),
        "matched_snp_id":     data.get("matched_snp_id"),
        "match_score":        data.get("match_score"),
        "verified":           False,
        "created_at":         datetime.utcnow().isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{REST_URL}/mse_profiles",
                json=payload,
                headers=_headers(),
            )
            res.raise_for_status()
            records = res.json()
            return records[0] if records else payload
    except Exception as e:
        print(f"[Supabase] insert_mse error: {e}")
        return None


async def list_mses(skip: int = 0, limit: int = 20) -> dict:
    """Fetch paginated list of MSE profiles from Supabase."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {**_headers(), "Range": f"{skip}-{skip + limit - 1}",
                       "Prefer": "count=exact"}
            res = await client.get(
                f"{REST_URL}/mse_profiles",
                params={"order": "created_at.desc"},
                headers=headers,
            )
            res.raise_for_status()
            records = res.json()
            content_range = res.headers.get("content-range", "0/0")
            total = int(content_range.split("/")[-1]) if "/" in content_range else len(records)
            return {"total": total, "mses": records}
    except Exception as e:
        print(f"[Supabase] list_mses error: {e}")
        return {"total": 0, "mses": []}


async def get_mse_by_id(mse_id: int) -> Optional[dict]:
    """Fetch single MSE profile by ID."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{REST_URL}/mse_profiles",
                params={"id": f"eq.{mse_id}"},
                headers=_headers(),
            )
            res.raise_for_status()
            records = res.json()
            return records[0] if records else None
    except Exception as e:
        print(f"[Supabase] get_mse_by_id error: {e}")
        return None
