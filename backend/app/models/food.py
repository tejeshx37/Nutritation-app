from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class Food(Base):
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255))
    
    # Nutrition per 100g
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    fiber_per_100g = Column(Float)
    sugar_per_100g = Column(Float)
    sodium_per_100g = Column(Float)
    
    # Additional nutrition info
    serving_size = Column(String(100))  # e.g., "1 cup", "100g"
    serving_weight_grams = Column(Float)
    
    # Food category
    category = Column(String(100))  # e.g., "grains", "vegetables", "fruits", "protein"
    subcategory = Column(String(100))  # e.g., "bread", "leafy greens", "berries", "chicken"
    
    # Indian food specific
    is_indian_food = Column(Boolean, default=False)
    regional_variants = Column(Text)  # JSON string of regional names
    
    # Source
    source = Column(String(50), default="fatsecret")  # fatsecret, user_created, etc.
    external_id = Column(String(100))  # ID from external API
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    food_logs = relationship("FoodLog", back_populates="food")
    
    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}', calories={self.calories_per_100g})>"


class FoodLog(Base):
    __tablename__ = "food_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    
    # Food consumption details
    quantity = Column(Float, nullable=False)  # e.g., 2.0
    unit = Column(String(50))  # e.g., "pieces", "grams", "cups"
    weight_grams = Column(Float)  # actual weight consumed
    
    # Meal context
    meal_type = Column(Enum(MealType), nullable=False)
    meal_time = Column(DateTime(timezone=True), nullable=False)
    
    # User notes
    notes = Column(Text)
    
    # Calculated nutrition (cached for performance)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="food_logs")
    food = relationship("Food", back_populates="food_logs")
    
    def __repr__(self):
        return f"<FoodLog(id={self.id}, user_id={self.user_id}, food='{self.food.name}', quantity={self.quantity})>"
    
    def calculate_nutrition(self):
        """Calculate nutrition values based on food and quantity"""
        if self.food and self.weight_grams:
            ratio = self.weight_grams / 100.0
            
            self.calories = (self.food.calories_per_100g or 0) * ratio
            self.protein = (self.food.protein_per_100g or 0) * ratio
            self.carbs = (self.food.carbs_per_100g or 0) * ratio
            self.fat = (self.food.fat_per_100g or 0) * ratio
            self.fiber = (self.food.fiber_per_100g or 0) * ratio
            self.sugar = (self.food.sugar_per_100g or 0) * ratio
            self.sodium = (self.food.sodium_per_100g or 0) * ratio
