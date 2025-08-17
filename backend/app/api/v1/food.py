from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, date, timedelta

from ...core.database import get_db
from ...models.user import User
from ...models.food import Food, FoodLog
from ...schemas.food import (
    FoodLogCreate, FoodLogResponse, FoodResponse, NaturalLanguageFoodEntry,
    ParsedFoodEntry, FoodSearchQuery
)
from ...services.nlp_service import nlp_service
from ...services.fatsecret_service import fatsecret_service
from ..v1.auth import get_current_user

router = APIRouter()


@router.post("/log", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_food(
    food_log: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log a food entry"""
    
    # Verify food exists
    result = await db.execute(select(Food).where(Food.id == food_log.food_id))
    food = result.scalar_one_or_none()
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    # Create food log entry
    food_log_entry = FoodLog(
        user_id=current_user.id,
        food_id=food_log.food_id,
        quantity=food_log.quantity,
        unit=food_log.unit,
        weight_grams=food_log.weight_grams,
        meal_type=food_log.meal_type,
        meal_time=food_log.meal_time,
        notes=food_log.notes
    )
    
    # Calculate nutrition values
    if food_log.weight_grams:
        food_log_entry.weight_grams = food_log.weight_grams
    else:
        # Convert quantity and unit to grams
        food_log_entry.weight_grams = nlp_service.convert_to_grams(
            food_log.quantity, food_log.unit
        )
    
    # Calculate nutrition
    food_log_entry.calculate_nutrition()
    
    db.add(food_log_entry)
    await db.commit()
    await db.refresh(food_log_entry)
    
    # Return response with food name
    return FoodLogResponse(
        id=food_log_entry.id,
        food_id=food_log_entry.food_id,
        food_name=food.name,
        quantity=food_log_entry.quantity,
        unit=food_log_entry.unit,
        weight_grams=food_log_entry.weight_grams,
        meal_type=food_log_entry.meal_type,
        meal_time=food_log_entry.meal_time,
        notes=food_log_entry.notes,
        calories=food_log_entry.calories,
        protein=food_log_entry.protein,
        carbs=food_log_entry.carbs,
        fat=food_log_entry.fat,
        fiber=food_log_entry.fiber,
        sugar=food_log_entry.sugar,
        sodium=food_log_entry.sodium,
        created_at=food_log_entry.created_at
    )


@router.post("/parse", response_model=ParsedFoodEntry)
async def parse_natural_language(
    food_entry: NaturalLanguageFoodEntry,
    current_user: User = Depends(get_current_user)
):
    """Parse natural language food entry using NLP"""
    
    try:
        parsed_entry = await nlp_service.parse_food_entry(
            food_entry.text, food_entry.meal_type
        )
        
        # Set meal time if not provided
        if not parsed_entry.meal_time:
            parsed_entry.meal_time = food_entry.meal_time or datetime.utcnow()
        
        return parsed_entry
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse food entry: {str(e)}"
        )


@router.post("/log-natural", response_model=List[FoodLogResponse], status_code=status.HTTP_201_CREATED)
async def log_natural_language(
    food_entry: NaturalLanguageFoodEntry,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log food using natural language entry with automatic parsing"""
    
    try:
        # Parse the natural language entry
        parsed_entry = await nlp_service.parse_food_entry(
            food_entry.text, food_entry.meal_type
        )
        
        logged_foods = []
        
        for food_item in parsed_entry.foods:
            # Search for the food in our database or FatSecret
            food = await _find_or_create_food(food_item.item, db)
            
            if food:
                # Create food log entry
                weight_grams = nlp_service.convert_to_grams(
                    food_item.quantity, food_item.unit
                )
                
                food_log = FoodLog(
                    user_id=current_user.id,
                    food_id=food.id,
                    quantity=food_item.quantity,
                    unit=food_item.unit,
                    weight_grams=weight_grams,
                    meal_type=parsed_entry.meal_type or food_entry.meal_type or "other",
                    meal_time=parsed_entry.meal_time or food_entry.meal_time or datetime.utcnow(),
                    notes=f"Parsed from: {food_entry.text}"
                )
                
                # Calculate nutrition
                food_log.calculate_nutrition()
                
                db.add(food_log)
                await db.commit()
                await db.refresh(food_log)
                
                # Add to response
                logged_foods.append(FoodLogResponse(
                    id=food_log.id,
                    food_id=food_log.food_id,
                    food_name=food.name,
                    quantity=food_log.quantity,
                    unit=food_log.unit,
                    weight_grams=food_log.weight_grams,
                    meal_type=food_log.meal_type,
                    meal_time=food_log.meal_time,
                    notes=food_log.notes,
                    calories=food_log.calories,
                    protein=food_log.protein,
                    carbs=food_log.carbs,
                    fat=food_log.fat,
                    fiber=food_log.fiber,
                    sugar=food_log.sugar,
                    sodium=food_log.sodium,
                    created_at=food_log.created_at
                ))
        
        return logged_foods
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log food entry: {str(e)}"
        )


@router.get("/search", response_model=List[FoodResponse])
async def search_foods(
    query: str,
    limit: int = 20,
    include_indian_foods: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for foods in database and FatSecret API"""
    
    foods = []
    
    # Search in local database first
    result = await db.execute(
        select(Food).where(
            Food.name.ilike(f"%{query}%")
        ).limit(limit)
    )
    local_foods = result.scalars().all()
    foods.extend(local_foods)
    
    # If we need more results, search FatSecret API
    if len(foods) < limit and fatsecret_service.access_token:
        try:
            fatsecret_foods = await fatsecret_service.search_foods(
                query, limit - len(foods)
            )
            foods.extend(fatsecret_foods)
        except Exception as e:
            print(f"FatSecret API search failed: {e}")
    
    return foods[:limit]


@router.get("/log/{log_id}", response_model=FoodLogResponse)
async def get_food_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific food log entry"""
    
    result = await db.execute(
        select(FoodLog).where(
            FoodLog.id == log_id,
            FoodLog.user_id == current_user.id
        )
    )
    food_log = result.scalar_one_or_none()
    
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found"
        )
    
    # Get food name
    food_result = await db.execute(select(Food).where(Food.id == food_log.food_id))
    food = food_result.scalar_one_or_none()
    
    return FoodLogResponse(
        id=food_log.id,
        food_id=food_log.food_id,
        food_name=food.name if food else "Unknown Food",
        quantity=food_log.quantity,
        unit=food_log.unit,
        weight_grams=food_log.weight_grams,
        meal_type=food_log.meal_type,
        meal_time=food_log.meal_time,
        notes=food_log.notes,
        calories=food_log.calories,
        protein=food_log.protein,
        carbs=food_log.carbs,
        fat=food_log.fat,
        fiber=food_log.fiber,
        sugar=food_log.sugar,
        sodium=food_log.sodium,
        created_at=food_log.created_at
    )


@router.get("/logs", response_model=List[FoodLogResponse])
async def get_user_food_logs(
    date: date = None,
    meal_type: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's food logs with optional filtering"""
    
    query = select(FoodLog).where(FoodLog.user_id == current_user.id)
    
    if date:
        query = query.where(FoodLog.meal_time >= date)
        query = query.where(FoodLog.meal_time < date + timedelta(days=1))
    
    if meal_type:
        query = query.where(FoodLog.meal_type == meal_type)
    
    query = query.order_by(FoodLog.meal_time.desc())
    
    result = await db.execute(query)
    food_logs = result.scalars().all()
    
    # Get food names for all logs
    food_ids = [log.food_id for log in food_logs]
    foods_result = await db.execute(select(Food).where(Food.id.in_(food_ids)))
    foods = {food.id: food for food in foods_result.scalars().all()}
    
    return [
        FoodLogResponse(
            id=log.id,
            food_id=log.food_id,
            food_name=foods.get(log.food_id, "Unknown Food").name,
            quantity=log.quantity,
            unit=log.unit,
            weight_grams=log.weight_grams,
            meal_type=log.meal_type,
            meal_time=log.meal_time,
            notes=log.notes,
            calories=log.calories,
            protein=log.protein,
            carbs=log.carbs,
            fat=log.fat,
            fiber=log.fiber,
            sugar=log.sugar,
            sodium=log.sodium,
            created_at=log.created_at
        )
        for log in food_logs
    ]


async def _find_or_create_food(food_name: str, db: AsyncSession) -> Food:
    """Find food in database or create new entry from FatSecret"""
    
    # First, try to find in local database
    result = await db.execute(
        select(Food).where(Food.name.ilike(f"%{food_name}%"))
    )
    existing_food = result.scalar_one_or_none()
    
    if existing_food:
        return existing_food
    
    # If not found locally, try FatSecret API
    if fatsecret_service.access_token:
        try:
            fatsecret_foods = await fatsecret_service.search_foods(food_name, 1)
            if fatsecret_foods:
                fatsecret_food = fatsecret_foods[0]
                
                # Create new food entry in local database
                new_food = Food(
                    name=fatsecret_food.name,
                    brand=fatsecret_food.brand,
                    calories_per_100g=fatsecret_food.calories_per_100g,
                    protein_per_100g=fatsecret_food.protein_per_100g,
                    carbs_per_100g=fatsecret_food.carbs_per_100g,
                    fat_per_100g=fatsecret_food.fat_per_100g,
                    fiber_per_100g=fatsecret_food.fiber_per_100g,
                    sugar_per_100g=fatsecret_food.sugar_per_100g,
                    sodium_per_100g=fatsecret_food.sodium_per_100g,
                    serving_size=fatsecret_food.serving_size,
                    serving_weight_grams=fatsecret_food.serving_weight_grams,
                    category=fatsecret_food.category,
                    subcategory=fatsecret_food.subcategory,
                    is_indian_food=fatsecret_food.is_indian_food,
                    source="fatsecret",
                    external_id=str(fatsecret_food.id)
                )
                
                db.add(new_food)
                await db.commit()
                await db.refresh(new_food)
                
                return new_food
        
        except Exception as e:
            print(f"Failed to create food from FatSecret: {e}")
    
    # If all else fails, create a basic food entry
    basic_food = Food(
        name=food_name,
        source="user_created",
        is_indian_food=False
    )
    
    db.add(basic_food)
    await db.commit()
    await db.refresh(basic_food)
    
    return basic_food
