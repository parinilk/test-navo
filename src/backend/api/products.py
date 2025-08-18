"""
Products API endpoints for Navo
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from models.database import get_database, COLLECTIONS

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ProductFilter(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    availability: Optional[str] = None
    rating_min: Optional[float] = None

class ProductSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    filters: Optional[ProductFilter] = None
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")

class Product(BaseModel):
    id: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    price_currency: Optional[str] = None
    availability: Optional[str] = None
    ratings_avg: Optional[float] = None
    ratings_count: Optional[int] = None
    description: Optional[str] = None

class ProductListResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    per_page: int
    has_next: bool

@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    availability: Optional[str] = Query(None, description="Filter by availability"),
    db=Depends(get_database)
):
    """List products with optional filters and pagination"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Build query
        query = {}
        
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        
        if brand:
            query["brand"] = {"$regex": brand, "$options": "i"}
        
        if price_min is not None or price_max is not None:
            price_filter = {}
            if price_min is not None:
                price_filter["$gte"] = price_min
            if price_max is not None:
                price_filter["$lte"] = price_max
            query["price"] = price_filter
        
        if availability:
            query["availability"] = {"$regex": availability, "$options": "i"}
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * limit
        cursor = collection.find(query).skip(skip).limit(limit)
        products_data = await cursor.to_list(length=limit)
        
        # Convert to response format
        products = []
        for product_data in products_data:
            product = Product(
                id=str(product_data["_id"]),
                product_name=product_data.get("product_name", ""),
                brand=product_data.get("brand"),
                category=product_data.get("category"),
                price=product_data.get("price"),
                price_currency=product_data.get("price_currency"),
                availability=product_data.get("availability"),
                ratings_avg=product_data.get("ratings_avg"),
                ratings_count=product_data.get("ratings_count"),
                description=product_data.get("description")
            )
            products.append(product)
        
        has_next = (skip + limit) < total
        
        response = ProductListResponse(
            products=products,
            total=total,
            page=page,
            per_page=limit,
            has_next=has_next
        )
        
        logger.info(f"Retrieved {len(products)} products (page {page})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error listing products: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving products")

@router.get("/{product_id}", response_model=Product)
async def get_product_details(
    product_id: str,
    db=Depends(get_database)
):
    """Get detailed information about a specific product"""
    try:
        from bson import ObjectId
        collection = db[COLLECTIONS["main_data"]]
        
        # Convert string ID to ObjectId
        try:
            object_id = ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid product ID format")
        
        # Find product
        product_data = await collection.find_one({"_id": object_id})
        
        if not product_data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Convert to response format
        product = Product(
            id=str(product_data["_id"]),
            product_name=product_data.get("product_name", ""),
            brand=product_data.get("brand"),
            category=product_data.get("category"),
            price=product_data.get("price"),
            price_currency=product_data.get("price_currency"),
            availability=product_data.get("availability"),
            ratings_avg=product_data.get("ratings_avg"),
            ratings_count=product_data.get("ratings_count"),
            description=product_data.get("description")
        )
        
        logger.info(f"Retrieved product details for ID: {product_id}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting product details: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving product details")

@router.post("/search", response_model=ProductListResponse)
async def search_products(
    request: ProductSearchRequest,
    db=Depends(get_database)
):
    """Search products using text search and filters"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Build query
        query = {}
        
        # Text search
        if request.query:
            query["$text"] = {"$search": request.query}
        
        # Apply filters
        if request.filters:
            if request.filters.category:
                query["category"] = {"$regex": request.filters.category, "$options": "i"}
            
            if request.filters.brand:
                query["brand"] = {"$regex": request.filters.brand, "$options": "i"}
            
            if request.filters.price_min is not None or request.filters.price_max is not None:
                price_filter = {}
                if request.filters.price_min is not None:
                    price_filter["$gte"] = request.filters.price_min
                if request.filters.price_max is not None:
                    price_filter["$lte"] = request.filters.price_max
                query["price"] = price_filter
            
            if request.filters.availability:
                query["availability"] = {"$regex": request.filters.availability, "$options": "i"}
            
            if request.filters.rating_min is not None:
                query["ratings_avg"] = {"$gte": request.filters.rating_min}
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Get results with relevance scoring if text search is used
        if request.query:
            # Include text score for relevance
            cursor = collection.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(request.limit)
        else:
            cursor = collection.find(query).limit(request.limit)
        
        products_data = await cursor.to_list(length=request.limit)
        
        # Convert to response format
        products = []
        for product_data in products_data:
            product = Product(
                id=str(product_data["_id"]),
                product_name=product_data.get("product_name", ""),
                brand=product_data.get("brand"),
                category=product_data.get("category"),
                price=product_data.get("price"),
                price_currency=product_data.get("price_currency"),
                availability=product_data.get("availability"),
                ratings_avg=product_data.get("ratings_avg"),
                ratings_count=product_data.get("ratings_count"),
                description=product_data.get("description")
            )
            products.append(product)
        
        response = ProductListResponse(
            products=products,
            total=total,
            page=1,
            per_page=request.limit,
            has_next=len(products) >= request.limit
        )
        
        logger.info(f"Search returned {len(products)} products for query: {request.query}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Error searching products")

@router.get("/categories/list")
async def list_categories(db=Depends(get_database)):
    """Get list of all available product categories"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Get distinct categories
        categories = await collection.distinct("category")
        
        # Filter out None/empty values and sort
        categories = [cat for cat in categories if cat]
        categories.sort()
        
        logger.info(f"Retrieved {len(categories)} categories")
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"❌ Error listing categories: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving categories")

@router.get("/brands/list")
async def list_brands(db=Depends(get_database)):
    """Get list of all available brands"""
    try:
        collection = db[COLLECTIONS["main_data"]]
        
        # Get distinct brands
        brands = await collection.distinct("brand")
        
        # Filter out None/empty values and sort
        brands = [brand for brand in brands if brand]
        brands.sort()
        
        logger.info(f"Retrieved {len(brands)} brands")
        return {"brands": brands}
        
    except Exception as e:
        logger.error(f"❌ Error listing brands: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving brands")
