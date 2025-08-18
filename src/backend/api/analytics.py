"""
Analytics API endpoints for Navo
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from models.database import get_database, COLLECTIONS

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for analytics
class TrendData(BaseModel):
    category: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    avg_price: float
    product_count: int
    top_brands: List[str]
    growth_percentage: Optional[float] = None

class CompetitiveAnalysisRequest(BaseModel):
    target_category: str
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    brands_to_compare: Optional[List[str]] = None

class CompetitiveAnalysisResponse(BaseModel):
    category: str
    total_products: int
    price_analysis: Dict[str, Any]
    brand_analysis: List[Dict[str, Any]]
    market_insights: List[str]

@router.get("/trends/{category}")
async def get_category_trends(
    category: str,
    db=Depends(get_database)
):
    """Get market trends for a specific category"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Get products in category
        category_query = {"category": {"$regex": category, "$options": "i"}}
        
        # Basic aggregation for trends
        pipeline = [
            {"$match": category_query},
            {
                "$group": {
                    "_id": "$brand",
                    "avg_price": {"$avg": "$price"},
                    "product_count": {"$sum": 1},
                    "avg_rating": {"$avg": "$ratings_avg"}
                }
            },
            {"$sort": {"product_count": -1}},
            {"$limit": 10}
        ]
        
        brand_stats = await collection.aggregate(pipeline).to_list(length=10)
        
        # Get overall category stats
        total_products = await collection.count_documents(category_query)
        
        avg_price_pipeline = [
            {"$match": category_query},
            {"$group": {"_id": None, "avg_price": {"$avg": "$price"}}}
        ]
        
        avg_price_result = await collection.aggregate(avg_price_pipeline).to_list(length=1)
        avg_price = avg_price_result[0]["avg_price"] if avg_price_result else 0
        
        # Get top brands
        top_brands = [brand["_id"] for brand in brand_stats[:5] if brand["_id"]]
        
        # Create trend response
        trend_data = TrendData(
            category=category,
            trend_direction="stable",  # You can implement trend calculation logic
            avg_price=round(avg_price, 2),
            product_count=total_products,
            top_brands=top_brands
        )
        
        logger.info(f"Generated trends for category: {category}")
        return {
            "category_trends": trend_data,
            "brand_breakdown": brand_stats,
            "analysis_timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting category trends: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving category trends")

@router.post("/competitive", response_model=CompetitiveAnalysisResponse)
async def competitive_analysis(
    request: CompetitiveAnalysisRequest,
    db=Depends(get_database)
):
    """Perform competitive analysis for a category"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Build base query
        query = {"category": {"$regex": request.target_category, "$options": "i"}}
        
        # Add price range filter if specified
        if request.price_range_min is not None or request.price_range_max is not None:
            price_filter = {}
            if request.price_range_min is not None:
                price_filter["$gte"] = request.price_range_min
            if request.price_range_max is not None:
                price_filter["$lte"] = request.price_range_max
            query["price"] = price_filter
        
        # Filter by brands if specified
        if request.brands_to_compare:
            query["brand"] = {"$in": request.brands_to_compare}
        
        # Get total products
        total_products = await collection.count_documents(query)
        
        # Price analysis
        price_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "avg_price": {"$avg": "$price"},
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"},
                    "median_price": {"$avg": "$price"}  # Simplified median
                }
            }
        ]
        
        price_stats = await collection.aggregate(price_pipeline).to_list(length=1)
        price_analysis = price_stats[0] if price_stats else {}
        
        # Brand analysis
        brand_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$brand",
                    "product_count": {"$sum": 1},
                    "avg_price": {"$avg": "$price"},
                    "avg_rating": {"$avg": "$ratings_avg"},
                    "total_reviews": {"$sum": "$ratings_count"}
                }
            },
            {"$sort": {"product_count": -1}},
            {"$limit": 20}
        ]
        
        brand_analysis = await collection.aggregate(brand_pipeline).to_list(length=20)
        
        # Generate market insights
        market_insights = []
        
        if brand_analysis:
            top_brand = brand_analysis[0]
            market_insights.append(f"Market leader: {top_brand['_id']} with {top_brand['product_count']} products")
            
            if len(brand_analysis) > 1:
                avg_brand_price = sum(b["avg_price"] for b in brand_analysis if b["avg_price"]) / len(brand_analysis)
                market_insights.append(f"Average brand price: ${avg_brand_price:.2f}")
        
        if price_analysis:
            price_range = price_analysis.get("max_price", 0) - price_analysis.get("min_price", 0)
            market_insights.append(f"Price range spans ${price_range:.2f}")
        
        market_insights.append(f"Total products analyzed: {total_products}")
        
        response = CompetitiveAnalysisResponse(
            category=request.target_category,
            total_products=total_products,
            price_analysis=price_analysis,
            brand_analysis=brand_analysis,
            market_insights=market_insights
        )
        
        logger.info(f"Completed competitive analysis for category: {request.target_category}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in competitive analysis: {e}")
        raise HTTPException(status_code=500, detail="Error performing competitive analysis")

@router.get("/summary")
async def get_market_summary(db=Depends(get_database)):
    """Get overall market summary statistics"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Total products
        total_products = await collection.count_documents({})
        
        # Category distribution
        category_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        categories = await collection.aggregate(category_pipeline).to_list(length=10)
        
        # Brand distribution
        brand_pipeline = [
            {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        brands = await collection.aggregate(brand_pipeline).to_list(length=10)
        
        # Price statistics
        price_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_price": {"$avg": "$price"},
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"}
                }
            }
        ]
        
        price_stats = await collection.aggregate(price_pipeline).to_list(length=1)
        
        summary = {
            "total_products": total_products,
            "top_categories": categories,
            "top_brands": brands,
            "price_statistics": price_stats[0] if price_stats else {},
            "last_updated": datetime.utcnow()
        }
        
        logger.info("Generated market summary")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Error generating market summary: {e}")
        raise HTTPException(status_code=500, detail="Error generating market summary")
