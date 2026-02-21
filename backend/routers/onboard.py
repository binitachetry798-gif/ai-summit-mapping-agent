from fastapi import APIRouter, HTTPException
from models.schemas import MSEOnboardRequest, MSEOnboardResponse
from services.classifier import classify_product
from services.matcher import find_best_snps
from services.supabase_client import insert_mse, list_mses

router = APIRouter(prefix="/onboard", tags=["Onboarding"])


@router.post(
    "/mse",
    response_model=MSEOnboardResponse,
    summary="Complete MSE onboarding with AI classification + SNP matching"
)
async def onboard_mse(request: MSEOnboardRequest):
    """
    Full MSE onboarding pipeline:
    1. Classifies product → ONDC taxonomy + HSN code (Gemini AI)
    2. Matches MSE profile → Top-3 SNPs via TF-IDF similarity
    3. Saves to Supabase database
    4. Returns classification result + best SNP recommendation
    """
    # Step 1: AI Classify
    classification = classify_product(request.product_description)

    # Step 2: SNP Match
    matches = find_best_snps(
        product_desc=request.product_description,
        location=f"{request.location}, {request.state}",
        capacity=request.annual_capacity,
        top_k=1,
    )
    best_match = matches[0] if matches else None

    # Step 3: Save to Supabase
    record = await insert_mse({
        "business_name":       request.business_name,
        "owner_name":          request.owner_name,
        "phone":               request.phone,
        "location":            request.location,
        "state":               request.state,
        "product_description": request.product_description,
        "annual_capacity":     request.annual_capacity,
        "preferred_language":  request.preferred_language,
        "udyam_number":        request.udyam_number,
        "ondc_category":       classification.get("category"),
        "ondc_subcategory":    classification.get("subcategory"),
        "hsn_code":            classification.get("hsn_code"),
        "matched_snp_id":      best_match["snp_id"] if best_match else None,
        "match_score":         best_match["final_score"] if best_match else None,
    })

    record_id = record.get("id", 0) if record else 0

    return MSEOnboardResponse(
        id=record_id,
        business_name=request.business_name,
        ondc_category=classification.get("category"),
        ondc_subcategory=classification.get("subcategory"),
        hsn_code=classification.get("hsn_code"),
        matched_snp=best_match,
        match_score=best_match["final_score"] if best_match else None,
        status="onboarded",
    )


@router.get("/mse/list", summary="List all onboarded MSEs from Supabase")
async def list_mse_profiles(skip: int = 0, limit: int = 20):
    """Returns paginated list of all onboarded MSEs from Supabase."""
    return await list_mses(skip=skip, limit=limit)
