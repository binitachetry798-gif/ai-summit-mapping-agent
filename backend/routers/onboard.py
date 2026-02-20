from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, MSEProfile
from models.schemas import MSEOnboardRequest, MSEOnboardResponse
from services.classifier import classify_product
from services.matcher import find_best_snps

router = APIRouter(prefix="/onboard", tags=["Onboarding"])


@router.post("/mse", response_model=MSEOnboardResponse, summary="Complete MSE onboarding with AI classification + SNP matching")
async def onboard_mse(request: MSEOnboardRequest, db: Session = Depends(get_db)):
    """
    Full MSE onboarding pipeline:
    1. Classifies product → ONDC taxonomy + HSN code
    2. Matches MSE profile → Top-3 SNPs via vector similarity
    3. Saves MSE profile to database
    4. Returns classification result + best SNP recommendation
    """
    # Step 1: Classify
    classification = classify_product(request.product_description)

    # Step 2: Match
    matches = find_best_snps(
        product_desc=request.product_description,
        location=f"{request.location}, {request.state}",
        capacity=request.annual_capacity,
        top_k=1
    )
    best_match = matches[0] if matches else None

    # Step 3: Save to DB
    mse = MSEProfile(
        business_name=request.business_name,
        owner_name=request.owner_name,
        phone=request.phone,
        location=request.location,
        state=request.state,
        product_description=request.product_description,
        annual_capacity=request.annual_capacity,
        preferred_language=request.preferred_language,
        udyam_number=request.udyam_number,
        ondc_category=classification.get("category"),
        ondc_subcategory=classification.get("subcategory"),
        hsn_code=classification.get("hsn_code"),
        matched_snp_id=best_match["snp_id"] if best_match else None,
        match_score=best_match["final_score"] if best_match else None,
    )
    db.add(mse)
    db.commit()
    db.refresh(mse)

    return MSEOnboardResponse(
        id=mse.id,
        business_name=mse.business_name,
        ondc_category=classification.get("category"),
        ondc_subcategory=classification.get("subcategory"),
        hsn_code=classification.get("hsn_code"),
        matched_snp=best_match,
        match_score=best_match["final_score"] if best_match else None,
        status="onboarded"
    )


@router.get("/mse/list", summary="List all onboarded MSEs")
async def list_mses(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Returns a paginated list of all onboarded MSEs."""
    mses = db.query(MSEProfile).offset(skip).limit(limit).all()
    return {
        "total": db.query(MSEProfile).count(),
        "mses": [
            {
                "id": m.id,
                "business_name": m.business_name,
                "location": f"{m.location}, {m.state}",
                "ondc_category": m.ondc_category,
                "matched_snp_id": m.matched_snp_id,
                "match_score": m.match_score,
                "verified": m.verified,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in mses
        ]
    }
