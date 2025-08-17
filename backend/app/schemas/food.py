from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class FoodItem(BaseModel):
    item: str
    quantity: float
    unit: str


class ParsedFoodEntry(BaseModel):
    foods: List[FoodItem]
    meal_type: Optional[MealType] = None
    meal_time: Optional[datetime] = None
    confidence: float = Field(..., ge=0, le=1)


class FoodLogCreate(BaseModel):
    food_id: int
    quantity: float = Field(..., gt=0)
    unit: str
    weight_grams: Optional[float] = None
    meal_type: MealType
    meal_time: datetime
    notes: Optional[str] = None


class FoodLogUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    weight_grams: Optional[float] = None
    meal_type: Optional[MealType] = None
    meal_time: Optional[datetime] = None
    notes: Optional[str] = None


class FoodLogResponse(BaseModel):
    id: int
    food_id: int
    food_name: str
    quantity: float
    unit: str
    weight_grams: Optional[float]
    meal_type: MealType
    meal_time: datetime
    notes: Optional[str]
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    sugar: float
    sodium: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class FoodResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    calories_per_100g: Optional[float]
    protein_per_100g: Optional[float]
    carbs_per_100g: Optional[float]
    fat_per_100g: Optional[float]
    fiber_per_100g: Optional[float]
    sugar_per_100g: Optional[float]
    sodium_per_100g: Optional[float]
    serving_size: Optional[str]
    serving_weight_grams: Optional[float]
    category: Optional[str]
    subcategory: Optional[str]
    is_indian_food: bool
    
    class Config:
        from_attributes = True


class NaturalLanguageFoodEntry(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    meal_type: Optional[MealType] = None
    meal_time: Optional[datetime] = None
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()


class FoodSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(10, ge=1, le=50)
    include_indian_foods: bool = True


class DailyNutritionSummary(BaseModel):
    date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_sugar_g: float
    total_sodium_mg: float
    calories_goal: Optional[int]
    protein_goal_g: Optional[float]
    carbs_goal_g: Optional[float]
    fat_goal_g: Optional[float]
    calories_progress: Optional[float]
    protein_progress: Optional[float]
    carbs_progress: Optional[float]
    fat_progress: Optional[float]
    total_meals: int
    total_snacks: int
    
    class Config:
        from_attributes = True


class NutritionGoalCreate(BaseModel):
    daily_calories: int = Field(..., gt=0)
    daily_protein_g: float = Field(..., gt=0)
    daily_carbs_g: float = Field(..., gt=0)
    daily_fat_g: float = Field(..., gt=0)
    daily_fiber_g: Optional[float] = Field(None, ge=0)
    daily_sugar_g: Optional[float] = Field(None, ge=0)
    daily_sodium_mg: Optional[float] = Field(None, ge=0)
    target_weight_kg: Optional[float] = Field(None, gt=0)
    weekly_weight_change_kg: Optional[float] = None
    daily_water_ml: Optional[int] = Field(None, gt=0)
    daily_steps: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    goal_type: str = Field(..., pattern="^(weight_loss|weight_gain|maintenance|muscle_gain)$")


class NutritionGoalResponse(BaseModel):
    id: int
    daily_calories: int
    daily_protein_g: float
    daily_carbs_g: float
    daily_fat_g: float
    daily_fiber_g: Optional[float]
    daily_sugar_g: Optional[float]
    daily_sodium_mg: Optional[float]
    target_weight_kg: Optional[float]
    weekly_weight_change_kg: Optional[float]
    daily_water_ml: Optional[int]
    daily_steps: Optional[int]
    description: Optional[str]
    goal_type: str
    is_active: bool
    start_date: date
    end_date: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True
