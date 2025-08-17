from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ...core.database import get_db
from ...models.user import User
from ...models.nutrition import NutritionGoal
from ...schemas.food import NutritionGoalCreate, NutritionGoalResponse
from ..v1.auth import get_current_user

router = APIRouter()


@router.post("/goals", response_model=NutritionGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_nutrition_goal(
    goal_data: NutritionGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new nutrition goal"""
    
    # Deactivate any existing active goals
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        )
    )
    existing_goals = result.scalars().all()
    
    for goal in existing_goals:
        goal.is_active = False
    
    # Create new goal
    nutrition_goal = NutritionGoal(
        user_id=current_user.id,
        daily_calories=goal_data.daily_calories,
        daily_protein_g=goal_data.daily_protein_g,
        daily_carbs_g=goal_data.daily_carbs_g,
        daily_fat_g=goal_data.daily_fat_g,
        daily_fiber_g=goal_data.daily_fiber_g,
        daily_sugar_g=goal_data.daily_sugar_g,
        daily_sodium_mg=goal_data.daily_sodium_mg,
        target_weight_kg=goal_data.target_weight_kg,
        weekly_weight_change_kg=goal_data.weekly_weight_change_kg,
        daily_water_ml=goal_data.daily_water_ml,
        daily_steps=goal_data.daily_steps,
        description=goal_data.description,
        goal_type=goal_data.goal_type,
        is_active=True
    )
    
    db.add(nutrition_goal)
    await db.commit()
    await db.refresh(nutrition_goal)
    
    return nutrition_goal


@router.get("/goals", response_model=List[NutritionGoalResponse])
async def get_nutrition_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all nutrition goals for the current user"""
    
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == current_user.id
        ).order_by(NutritionGoal.created_at.desc())
    )
    
    return result.scalars().all()


@router.get("/goals/current", response_model=NutritionGoalResponse)
async def get_current_nutrition_goal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current active nutrition goal"""
    
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        )
    )
    
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active nutrition goal found"
        )
    
    return goal


@router.put("/goals/{goal_id}", response_model=NutritionGoalResponse)
async def update_nutrition_goal(
    goal_id: int,
    goal_update: NutritionGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a nutrition goal"""
    
    # Find the goal
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == current_user.id
        )
    )
    
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition goal not found"
        )
    
    # Update goal fields
    for field, value in goal_update.dict().items():
        setattr(goal, field, value)
    
    await db.commit()
    await db.refresh(goal)
    
    return goal


@router.delete("/goals/{goal_id}")
async def delete_nutrition_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a nutrition goal"""
    
    # Find the goal
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == current_user.id
        )
    )
    
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition goal not found"
        )
    
    # Soft delete by setting as inactive
    goal.is_active = False
    await db.commit()
    
    return {"message": "Nutrition goal deleted successfully"}


@router.post("/goals/{goal_id}/activate")
async def activate_nutrition_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a specific nutrition goal"""
    
    # Find the goal
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == current_user.id
        )
    )
    
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition goal not found"
        )
    
    # Deactivate all other goals
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        )
    )
    active_goals = result.scalars().all()
    
    for active_goal in active_goals:
        active_goal.is_active = False
    
    # Activate the selected goal
    goal.is_active = True
    await db.commit()
    
    return {"message": "Nutrition goal activated successfully"}
