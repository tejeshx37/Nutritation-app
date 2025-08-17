from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime, date, timedelta

from ...core.database import get_db
from ...models.user import User
from ...models.food import FoodLog, MealType
from ...models.nutrition import DailyNutritionSummary, NutritionGoal
from ...schemas.food import DailyNutritionSummary as DailyNutritionSummarySchema
from ...schemas.food import FoodLogResponse
from ..v1.auth import get_current_user

router = APIRouter()


@router.get("/summary/{target_date}", response_model=DailyNutritionSummarySchema)
async def get_daily_nutrition_summary(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily nutrition summary for a specific date"""
    
    # Get or create daily summary
    summary = await _get_or_create_daily_summary(current_user.id, target_date, db)
    
    return DailyNutritionSummarySchema(
        date=summary.date,
        total_calories=summary.total_calories,
        total_protein_g=summary.total_protein_g,
        total_carbs_g=summary.total_carbs_g,
        total_fat_g=summary.total_fat_g,
        total_fiber_g=summary.total_fiber_g,
        total_sugar_g=summary.total_sugar_g,
        total_sodium_mg=summary.total_sodium_mg,
        calories_goal=summary.calories_goal,
        protein_goal_g=summary.protein_goal_g,
        carbs_goal_g=summary.carbs_goal_g,
        fat_goal_g=summary.fat_goal_g,
        calories_progress=summary.calories_progress,
        protein_progress=summary.protein_progress,
        carbs_progress=summary.carbs_progress,
        fat_progress=summary.fat_progress,
        total_meals=summary.total_meals,
        total_snacks=summary.total_snacks
    )


@router.get("/summary", response_model=DailyNutritionSummarySchema)
async def get_today_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's nutrition summary"""
    today = date.today()
    return await get_daily_nutrition_summary(today, current_user, db)


@router.get("/weekly-summary")
async def get_weekly_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly nutrition summary"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    summaries = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        summary = await _get_or_create_daily_summary(current_user.id, current_date, db)
        
        summaries.append({
            "date": summary.date.isoformat(),
            "calories": summary.total_calories,
            "protein": summary.total_protein_g,
            "carbs": summary.total_carbs_g,
            "fat": summary.total_fat_g,
            "calories_progress": summary.calories_progress,
            "protein_progress": summary.protein_progress,
            "carbs_progress": summary.carbs_progress,
            "fat_progress": summary.fat_progress
        })
    
    return {
        "week_start": start_date.isoformat(),
        "week_end": end_date.isoformat(),
        "summaries": summaries
    }


@router.get("/monthly-summary")
async def get_monthly_summary(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get monthly nutrition summary"""
    
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get all food logs for the month
    result = await db.execute(
        select(FoodLog).where(
            FoodLog.user_id == current_user.id,
            FoodLog.meal_time >= start_date,
            FoodLog.meal_time <= end_date + timedelta(days=1)
        )
    )
    food_logs = result.scalars().all()
    
    # Calculate monthly totals
    monthly_totals = {
        "calories": sum(log.calories or 0 for log in food_logs),
        "protein": sum(log.protein or 0 for log in food_logs),
        "carbs": sum(log.carbs or 0 for log in food_logs),
        "fat": sum(log.fat or 0 for log in food_logs),
        "fiber": sum(log.fiber or 0 for log in food_logs),
        "sugar": sum(log.sugar or 0 for log in food_logs),
        "sodium": sum(log.sodium or 0 for log in food_logs)
    }
    
    # Calculate daily averages
    days_in_month = (end_date - start_date).days + 1
    daily_averages = {
        key: value / days_in_month for key, value in monthly_totals.items()
    }
    
    # Get meal type distribution
    meal_counts = {}
    for log in food_logs:
        meal_type = log.meal_type.value
        meal_counts[meal_type] = meal_counts.get(meal_type, 0) + 1
    
    return {
        "year": year,
        "month": month,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days_in_month": days_in_month,
        "monthly_totals": monthly_totals,
        "daily_averages": daily_averages,
        "meal_distribution": meal_counts,
        "total_entries": len(food_logs)
    }


@router.get("/progress")
async def get_progress_data(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get progress data for charts"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get daily summaries for the period
    result = await db.execute(
        select(DailyNutritionSummary).where(
            DailyNutritionSummary.user_id == current_user.id,
            DailyNutritionSummary.date >= start_date,
            DailyNutritionSummary.date <= end_date
        ).order_by(DailyNutritionSummary.date)
    )
    summaries = result.scalars().all()
    
    # Prepare chart data
    chart_data = {
        "labels": [],
        "calories": [],
        "protein": [],
        "carbs": [],
        "fat": [],
        "calories_goal": [],
        "protein_goal": [],
        "carbs_goal": [],
        "fat_goal": []
    }
    
    # Fill in missing dates with zero values
    current_date = start_date
    summary_dict = {summary.date: summary for summary in summaries}
    
    while current_date <= end_date:
        chart_data["labels"].append(current_date.strftime("%m/%d"))
        
        if current_date in summary_dict:
            summary = summary_dict[current_date]
            chart_data["calories"].append(summary.total_calories)
            chart_data["protein"].append(summary.total_protein_g)
            chart_data["carbs"].append(summary.total_carbs_g)
            chart_data["fat"].append(summary.total_fat_g)
            chart_data["calories_goal"].append(summary.calories_goal)
            chart_data["protein_goal"].append(summary.protein_goal_g)
            chart_data["carbs_goal"].append(summary.carbs_goal_g)
            chart_data["fat_goal"].append(summary.fat_goal_g)
        else:
            # Fill with zeros for missing dates
            chart_data["calories"].append(0)
            chart_data["protein"].append(0)
            chart_data["carbs"].append(0)
            chart_data["fat"].append(0)
            chart_data["calories_goal"].append(0)
            chart_data["protein_goal"].append(0)
            chart_data["carbs_goal"].append(0)
            chart_data["fat_goal"].append(0)
        
        current_date += timedelta(days=1)
    
    return chart_data


@router.get("/insights")
async def get_nutrition_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered nutrition insights"""
    
    # Get recent food logs (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    result = await db.execute(
        select(FoodLog).where(
            FoodLog.user_id == current_user.id,
            FoodLog.meal_time >= start_date,
            FoodLog.meal_time <= end_date
        ).order_by(FoodLog.meal_time.desc())
    )
    recent_logs = result.scalars().all()
    
    # Get current nutrition goals
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        )
    )
    current_goal = result.scalar_one_or_none()
    
    insights = []
    
    if recent_logs:
        # Calculate averages
        total_calories = sum(log.calories or 0 for log in recent_logs)
        total_protein = sum(log.protein or 0 for log in recent_logs)
        total_carbs = sum(log.carbs or 0 for log in recent_logs)
        total_fat = sum(log.fat or 0 for log in recent_logs)
        
        avg_calories = total_calories / 7
        avg_protein = total_protein / 7
        avg_carbs = total_carbs / 7
        avg_fat = total_fat / 7
        
        # Generate insights
        if current_goal:
            if avg_calories < current_goal.daily_calories * 0.8:
                insights.append({
                    "type": "warning",
                    "title": "Low Calorie Intake",
                    "message": f"Your average daily calories ({avg_calories:.0f}) are below your goal ({current_goal.daily_calories}). Consider adding healthy snacks or increasing portion sizes."
                })
            
            if avg_protein < current_goal.daily_protein_g * 0.8:
                insights.append({
                    "type": "warning",
                    "title": "Low Protein Intake",
                    "message": f"Your average daily protein ({avg_protein:.1f}g) is below your goal ({current_goal.daily_protein_g}g). Consider adding more protein-rich foods like eggs, chicken, or legumes."
                })
        
        # Meal timing insights
        meal_times = [log.meal_time for log in recent_logs]
        if meal_times:
            earliest_meal = min(meal_times)
            latest_meal = max(meal_times)
            
            if (latest_meal - earliest_meal).total_seconds() > 16 * 3600:  # 16 hours
                insights.append({
                    "type": "info",
                    "title": "Extended Eating Window",
                    "message": "Your eating window spans more than 16 hours. Consider reducing this to 12-14 hours for better metabolic health."
                })
    
    # Add general insights
    insights.extend([
        {
            "type": "tip",
            "title": "Stay Hydrated",
            "message": "Remember to drink at least 8 glasses of water daily for optimal health."
        },
        {
            "type": "tip",
            "title": "Balanced Meals",
            "message": "Try to include protein, healthy fats, and complex carbohydrates in each meal."
        }
    ])
    
    return {
        "insights": insights,
        "period": "7 days",
        "total_entries": len(recent_logs)
    }


async def _get_or_create_daily_summary(user_id: int, target_date: date, db: AsyncSession) -> DailyNutritionSummary:
    """Get or create daily nutrition summary for a user and date"""
    
    # Try to find existing summary
    result = await db.execute(
        select(DailyNutritionSummary).where(
            DailyNutritionSummary.user_id == user_id,
            DailyNutritionSummary.date == target_date
        )
    )
    summary = result.scalar_one_or_none()
    
    if summary:
        return summary
    
    # Create new summary
    summary = DailyNutritionSummary(
        user_id=user_id,
        date=target_date
    )
    
    # Get food logs for the date
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    result = await db.execute(
        select(FoodLog).where(
            FoodLog.user_id == user_id,
            FoodLog.meal_time >= start_datetime,
            FoodLog.meal_time <= end_datetime
        )
    )
    food_logs = result.scalars().all()
    
    # Calculate totals
    summary.total_calories = sum(log.calories or 0 for log in food_logs)
    summary.total_protein_g = sum(log.protein or 0 for log in food_logs)
    summary.total_carbs_g = sum(log.carbs or 0 for log in food_logs)
    summary.total_fat_g = sum(log.fat or 0 for log in food_logs)
    summary.total_fiber_g = sum(log.fiber or 0 for log in food_logs)
    summary.total_sugar_g = sum(log.sugar or 0 for log in food_logs)
    summary.total_sodium_mg = sum(log.sodium or 0 for log in food_logs)
    
    # Count meals and snacks
    summary.total_meals = sum(1 for log in food_logs if log.meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER])
    summary.total_snacks = sum(1 for log in food_logs if log.meal_type == MealType.SNACK)
    
    # Get current nutrition goals
    result = await db.execute(
        select(NutritionGoal).where(
            NutritionGoal.user_id == user_id,
            NutritionGoal.is_active == True
        )
    )
    current_goal = result.scalar_one_or_none()
    
    if current_goal:
        summary.calories_goal = current_goal.daily_calories
        summary.protein_goal_g = current_goal.daily_protein_g
        summary.carbs_goal_g = current_goal.daily_carbs_g
        summary.fat_goal_g = current_goal.daily_fat_g
        
        # Calculate progress
        summary.calculate_progress()
    
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    
    return summary
