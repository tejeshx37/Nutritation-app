import React from 'react';
import { TrendingUp, Target, Utensils, Activity } from 'lucide-react';

interface NutritionSummary {
  total_calories?: number;
  total_protein_g?: number;
  total_carbs_g?: number;
  total_fat_g?: number;
  total_fiber_g?: number;
  total_sugar_g?: number;
  total_sodium_mg?: number;
  calories_goal?: number;
  protein_goal_g?: number;
  carbs_goal_g?: number;
  fat_goal_g?: number;
  calories_progress?: number;
  protein_progress?: number;
  carbs_progress?: number;
  fat_progress?: number;
}

interface NutritionSummaryCardProps {
  summary?: NutritionSummary;
}

const NutritionSummaryCard: React.FC<NutritionSummaryCardProps> = ({ summary }) => {
  if (!summary) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Today's Nutrition</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No nutrition data available for today</p>
          <p className="text-sm">Start logging your food to see your progress!</p>
        </div>
      </div>
    );
  }

  const nutritionItems = [
    {
      label: 'Calories',
      value: summary.total_calories || 0,
      goal: summary.calories_goal,
      progress: summary.calories_progress,
      icon: TrendingUp,
      color: 'nutrition-calories',
      unit: ''
    },
    {
      label: 'Protein',
      value: summary.total_protein_g || 0,
      goal: summary.protein_goal_g,
      progress: summary.protein_progress,
      icon: Target,
      color: 'nutrition-protein',
      unit: 'g'
    },
    {
      label: 'Carbs',
      value: summary.total_carbs_g || 0,
      goal: summary.carbs_goal_g,
      progress: summary.carbs_progress,
      icon: Utensils,
      color: 'nutrition-carbs',
      unit: 'g'
    },
    {
      label: 'Fat',
      value: summary.total_fat_g || 0,
      goal: summary.fat_goal_g,
      progress: summary.fat_progress,
      icon: Activity,
      color: 'nutrition-fat',
      unit: 'g'
    }
  ];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Today's Nutrition Summary</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {nutritionItems.map((item) => {
          const Icon = item.icon;
          const progress = item.progress || 0;
          const goal = item.goal || 0;
          
          return (
            <div key={item.label} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-6 h-6 bg-${item.color} rounded-lg flex items-center justify-center`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                  <span className="font-medium text-gray-700">{item.label}</span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-gray-900">
                    {item.value.toFixed(item.label === 'Calories' ? 0 : 1)}{item.unit}
                  </div>
                  {goal > 0 && (
                    <div className="text-sm text-gray-500">
                      of {goal.toFixed(item.label === 'Calories' ? 0 : 1)}{item.unit}
                    </div>
                  )}
                </div>
              </div>
              
              {goal > 0 && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium text-gray-900">{progress.toFixed(1)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className={`progress-fill ${item.label.toLowerCase()}`}
                      style={{ 
                        width: `${Math.min(progress, 100)}%`,
                        backgroundColor: `var(--color-${item.color.replace('nutrition-', '')})`
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Additional Nutrition Info */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-gray-500">Fiber</div>
            <div className="font-semibold text-gray-900">
              {(summary.total_fiber_g || 0).toFixed(1)}g
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-500">Sugar</div>
            <div className="font-semibold text-gray-900">
              {(summary.total_sugar_g || 0).toFixed(1)}g
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-500">Sodium</div>
            <div className="font-semibold text-gray-900">
              {(summary.total_sodium_mg || 0).toFixed(0)}mg
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NutritionSummaryCard;
