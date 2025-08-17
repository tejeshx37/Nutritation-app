from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
from datetime import date


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Goal period
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    # Daily nutrition targets
    daily_calories = Column(Integer, nullable=False)
    daily_protein_g = Column(Float, nullable=False)
    daily_carbs_g = Column(Float, nullable=False)
    daily_fat_g = Column(Float, nullable=False)
    daily_fiber_g = Column(Float)
    daily_sugar_g = Column(Float)
    daily_sodium_mg = Column(Float)
    
    # Weight goals
    target_weight_kg = Column(Float)
    weekly_weight_change_kg = Column(Float)  # positive for gain, negative for loss
    
    # Additional goals
    daily_water_ml = Column(Integer)
    daily_steps = Column(Integer)
    
    # Goal description
    description = Column(Text)
    goal_type = Column(String(50))  # weight_loss, weight_gain, maintenance, muscle_gain
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="nutrition_goals")
    
    def __repr__(self):
        return f"<NutritionGoal(id={self.id}, user_id={self.user_id}, calories={self.daily_calories})>"


class DailyNutritionSummary(Base):
    __tablename__ = "daily_nutrition_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    
    # Actual nutrition consumed
    total_calories = Column(Float, default=0)
    total_protein_g = Column(Float, default=0)
    total_carbs_g = Column(Float, default=0)
    total_fat_g = Column(Float, default=0)
    total_fiber_g = Column(Float, default=0)
    total_sugar_g = Column(Float, default=0)
    total_sodium_mg = Column(Float, default=0)
    
    # Goal vs actual
    calories_goal = Column(Integer)
    protein_goal_g = Column(Float)
    carbs_goal_g = Column(Float)
    fat_goal_g = Column(Float)
    
    # Progress percentages
    calories_progress = Column(Float)  # percentage of goal achieved
    protein_progress = Column(Float)
    carbs_progress = Column(Float)
    fat_progress = Column(Float)
    
    # Additional metrics
    total_meals = Column(Integer, default=0)
    total_snacks = Column(Integer, default=0)
    water_intake_ml = Column(Integer, default=0)
    steps_taken = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DailyNutritionSummary(id={self.id}, user_id={self.user_id}, date={self.date})>"
    
    def calculate_progress(self):
        """Calculate progress percentages for each nutrition goal"""
        if self.calories_goal and self.calories_goal > 0:
            self.calories_progress = min((self.total_calories / self.calories_goal) * 100, 100)
        
        if self.protein_goal_g and self.protein_goal_g > 0:
            self.protein_progress = min((self.total_protein_g / self.protein_goal_g) * 100, 100)
        
        if self.carbs_goal_g and self.carbs_goal_g > 0:
            self.carbs_progress = min((self.total_carbs_g / self.carbs_goal_g) * 100, 100)
        
        if self.fat_goal_g and self.fat_goal_g > 0:
            self.fat_progress = min((self.total_fat_g / self.fat_goal_g) * 100, 100)
