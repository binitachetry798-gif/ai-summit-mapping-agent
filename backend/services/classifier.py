"""
AI Product Classifier Service
Uses Google Gemini API for zero-shot ONDC taxonomy classification.
Falls back to keyword-based classification if API key is not configured.
"""
import os
import re
import json
from typing import Tuple, List
from dotenv import load_dotenv

load_dotenv()

# ─── ONDC Taxonomy with HSN Codes ───────────────────────────────────────────

ONDC_TAXONOMY = {
    "Fashion & Footwear": {
        "subcategories": [
            "Ethnic Wear", "Western Wear", "Sarees & Dupatta",
            "Leather Footwear", "Ethnic Footwear", "Accessories"
        ],
        "hsn_range": ["6101", "6402", "6403", "6217"],
        "keywords": ["saree", "salwar", "kurta", "dupatta", "shawl", "chappal",
                     "sandal", "shoe", "leather", "silk", "cotton wear", "ethnic",
                     "blouse", "lehenga", "dhoti", "lungi", "kurtis", "hand loom"]
    },
    "Home & Kitchen": {
        "subcategories": [
            "Handicrafts", "Wooden Furniture", "Brass & Copper Items",
            "Pottery & Ceramics", "Home Decor", "Kitchen Utensils"
        ],
        "hsn_range": ["6911", "7418", "9403"],
        "keywords": ["pottery", "ceramic", "brass", "wooden", "furniture",
                     "handicraft", "decor", "lamp", "idol", "statue", "utensil",
                     "vessel", "earthen", "terracotta", "bamboo", "cane", "wicker"]
    },
    "Food & Beverage": {
        "subcategories": [
            "Organic Food", "Spices & Condiments", "Grains & Pulses",
            "Pickles & Preserves", "Dairy Products", "Snacks & Sweets"
        ],
        "hsn_range": ["0904", "1001", "2001"],
        "keywords": ["spice", "masala", "pickle", "grain", "pulse", "rice",
                     "wheat", "flour", "dal", "chutney", "murabba", "ladoo",
                     "snack", "namkeen", "organic", "natural food", "dairy", "ghee"]
    },
    "Beauty & Personal Care": {
        "subcategories": [
            "Ayurvedic Products", "Herbal Cosmetics", "Natural Skincare",
            "Essential Oils", "Hair Care", "Wellness Products"
        ],
        "hsn_range": ["3304", "3305", "3306"],
        "keywords": ["ayurvedic", "herbal", "skincare", "hair oil", "essential oil",
                     "lotion", "cream", "face pack", "ubtan", "soap", "shampoo",
                     "wellness", "natural", "organic beauty", "kumkumadi", "neem"]
    },
    "Engineering & Auto Parts": {
        "subcategories": [
            "Auto Ancillary Parts", "Industrial Hardware", "Metal Fabrication",
            "Machined Components", "Electrical Components"
        ],
        "hsn_range": ["8708", "7326", "8536"],
        "keywords": ["auto part", "component", "hardware", "fabrication", "machined",
                     "casting", "forging", "valve", "pump", "gear", "bearing",
                     "sheet metal", "welding", "bolt", "nut", "electrical"]
    },
    "Jewellery & Accessories": {
        "subcategories": [
            "Silver Jewellery", "Gold Ornaments", "Imitation Jewellery",
            "Tribal Jewellery", "Gemstones", "Fashion Accessories"
        ],
        "hsn_range": ["7113", "7117"],
        "keywords": ["jewellery", "jewelry", "silver", "gold", "necklace", "bracelet",
                     "earring", "ring", "bangle", "anklet", "gem", "stone", "filigree",
                     "meenakari", "kundan", "polki", "imitation"]
    },
    "Grocery & Staples": {
        "subcategories": [
            "Packaged Staples", "Edible Oils", "Tea & Coffee", "Dry Fruits", "Honey"
        ],
        "hsn_range": ["1516", "0902", "0812"],
        "keywords": ["grocery", "staples", "edible oil", "mustard oil", "tea",
                     "coffee", "sugar", "salt", "honey", "dry fruit", "almond",
                     "cashew", "walnut", "dates", "raisin"]
    },
    "Packaging & Paper Products": {
        "subcategories": [
            "Corrugated Packaging", "Paper Bags", "Eco Packaging", "Gift Wrap"
        ],
        "hsn_range": ["4819", "4802"],
        "keywords": ["packaging", "carton", "box", "paper bag", "gift wrap",
                     "corrugated", "cardboard", "eco packaging", "biodegradable"]
    }
}

# ─── Gemini Classifier ───────────────────────────────────────────────────────

_gemini_client = None

def _get_gemini_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception as e:
        print(f"[Classifier] Gemini init failed: {e}")
        return None


def _gemini_classify(description: str) -> dict | None:
    client = _get_gemini_client()
    if client is None:
        return None

    categories_str = "\n".join([f"- {cat}" for cat in ONDC_TAXONOMY.keys()])
    prompt = f"""You are an expert Indian ONDC product taxonomy classifier.

Given an MSE product description, return a JSON object with:
- "category": one of the main ONDC categories below
- "subcategory": most specific relevant subcategory
- "hsn_code": best matching 4-digit HSN code
- "confidence": float 0-1
- "keywords": list of 3-5 key product features

ONDC Categories:
{categories_str}

Product Description: "{description}"

Respond ONLY with a valid JSON object, no markdown, no explanation.
"""
    try:
        from google import genai as _genai
        # Try models in order of preference
        models_to_try = [
            "gemini-2.5-pro-preview-03-25",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-pro",
        ]
        response = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                break
            except Exception:
                continue
        if response is None:
            return None
        raw = response.text.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"[Classifier] Gemini classify error: {e}")
        return None



def _keyword_classify(description: str) -> dict:
    """Fallback keyword-based classifier"""
    desc_lower = description.lower()
    best_cat = "Home & Kitchen"
    best_score = 0
    best_sub = "Handicrafts"
    best_hsn = "9999"

    for cat, info in ONDC_TAXONOMY.items():
        score = sum(1 for kw in info["keywords"] if kw in desc_lower)
        if score > best_score:
            best_score = score
            best_cat = cat
            best_hsn = info["hsn_range"][0]
            # Pick subcategory based on keyword overlap
            for sub in info["subcategories"]:
                if any(w in desc_lower for w in sub.lower().split()):
                    best_sub = sub
                    break
            else:
                best_sub = info["subcategories"][0]

    # Extract simple keywords
    words = [w for w in desc_lower.split() if len(w) > 3]
    keywords = list(set(words))[:5]

    confidence = min(0.4 + best_score * 0.1, 0.85)

    return {
        "category": best_cat,
        "subcategory": best_sub,
        "hsn_code": best_hsn,
        "confidence": round(confidence, 2),
        "keywords": keywords
    }


def classify_product(description: str) -> dict:
    """
    Main classifier entry point.
    Tries Gemini first, falls back to keyword matcher.
    """
    result = _gemini_classify(description)
    if result and "category" in result:
        # Validate category is in taxonomy
        if result["category"] not in ONDC_TAXONOMY:
            result["category"] = list(ONDC_TAXONOMY.keys())[0]
        result["confidence"] = float(result.get("confidence", 0.9))
        result.setdefault("keywords", [])
        return result
    return _keyword_classify(description)
