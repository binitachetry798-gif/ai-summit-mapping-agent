from fastapi import APIRouter, Query, HTTPException
from models.schemas import SNPMatchResponse
from services.matcher import find_best_snps, get_total_snp_count
from typing import Optional

router = APIRouter(prefix="/match", tags=["SNP Matching"])


@router.get("/snp", response_model=SNPMatchResponse, summary="Match MSE to best-fit SNP partners")
async def match_snp(
    product_desc: str = Query(..., description="MSE product description"),
    location: Optional[str] = Query(None, description="City/State of MSE"),
    capacity: Optional[int] = Query(None, description="Annual production capacity in units"),
    top_k: int = Query(3, ge=1, le=8, description="Number of SNP matches to return")
):
    """
    Matches an MSE product description against registered SNPs using
    Sentence-Transformers cosine similarity + operational capacity weighting.
    Returns top-k SNPs ranked by a final weighted score.
    """
    if not product_desc.strip():
        raise HTTPException(status_code=400, detail="product_desc is required")

    total = get_total_snp_count()
    matches = find_best_snps(product_desc, location, capacity, top_k)

    return SNPMatchResponse(
        query=product_desc,
        matches=matches,
        total_snps_evaluated=total
    )
