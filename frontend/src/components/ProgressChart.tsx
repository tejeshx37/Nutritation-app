import React from 'react';
import { TrendingUp, Target, Utensils, Activity } from 'lucide-react';

interface ProgressData {
  labels: string[];
  calories: number[];
  protein: number[];
  carbs: number[];
  fat: number[];
  calories_goal: number[];
  protein_goal: number[];
  carbs_goal: number[];
  fat_goal: number[];
}

interface ProgressChartProps {
  data: ProgressData;
}

const ProgressChart: React.FC<ProgressChartProps> = ({ data }) => {
  if (!data || !data.labels || data.labels.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p>No progress data available</p>
        <p className="text-sm">Start logging your food to see your progress over time!</p>
      </div>
    );
  }

  const maxCalories = Math.max(...data.calories, ...data.calories_goal);
  const maxProtein = Math.max(...data.protein, ...data.protein_goal);
  const maxCarbs = Math.max(...data.carbs, ...data.carbs_goal);
  const maxFat = Math.max(...data.fat, ...data.fat_goal);

  const nutritionMetrics = [
    {
      label: 'Calories',
      data: data.calories,
      goal: data.calories_goal,
      max: maxCalories,
      icon: TrendingUp,
      color: 'nutrition-calories',
      unit: ''
    },
    {
      label: 'Protein',
      data: data.protein,
      goal: data.protein_goal,
      max: maxProtein,
      icon: Target,
      color: 'nutrition-protein',
      unit: 'g'
    },
    {
      label: 'Carbs',
      data: data.carbs,
      goal: data.carbs_goal,
      max: maxCarbs,
      icon: Utensils,
      color: 'nutrition-carbs',
      unit: 'g'
    },
    {
      label: 'Fat',
      data: data.fat,
      goal: data.fat_goal,
      max: maxFat,
      icon: Activity,
      color: 'nutrition-fat',
      unit: 'g'
    }
  ];

  return (
    <div className="space-y-6">
      {nutritionMetrics.map((metric) => (
        <div key={metric.label} className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-5 h-5 bg-${metric.color} rounded-lg flex items-center justify-center`}>
                <metric.icon className="h-3 w-3 text-white" />
              </div>
              <span className="font-medium text-gray-700">{metric.label}</span>
            </div>
            <div className="text-sm text-gray-500">
              Max: {metric.max.toFixed(metric.label === 'Calories' ? 0 : 1)}{metric.unit}
            </div>
          </div>
          
          {/* Chart Bars */}
          <div className="space-y-2">
            {data.labels.map((label, index) => {
              const value = metric.data[index] || 0;
              const goal = metric.goal[index] || 0;
              const height = metric.max > 0 ? (value / metric.max) * 100 : 0;
              const goalHeight = metric.max > 0 ? (goal / metric.max) * 100 : 0;
              
              return (
                <div key={label} className="flex items-center space-x-3">
                  <div className="w-16 text-xs text-gray-500 text-right">
                    {label}
                  </div>
                  
                  <div className="flex-1 relative">
                    <div className="h-8 bg-gray-100 rounded-lg relative overflow-hidden">
                      {/* Goal line */}
                      {goal > 0 && (
                        <div 
                          className="absolute top-0 left-0 w-full h-0.5 bg-gray-400"
                          style={{ top: `${Math.min(goalHeight, 100)}%` }}
                        ></div>
                      )}
                      
                      {/* Actual value bar */}
                      <div 
                        className={`h-full bg-${metric.color} rounded-lg transition-all duration-300`}
                        style={{ 
                          width: `${Math.min(height, 100)}%`,
                          backgroundColor: `var(--color-${metric.color.replace('nutrition-', '')})`
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="w-16 text-xs text-gray-900 text-right">
                    {value.toFixed(metric.label === 'Calories' ? 0 : 1)}{metric.unit}
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Legend */}
          <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <div className={`w-3 h-3 bg-${metric.color} rounded`}></div>
              <span>Actual</span>
            </div>
            {metric.goal.some(g => g > 0) && (
              <div className="flex items-center space-x-1">
                <div className="w-3 h-0.5 bg-gray-400"></div>
                <span>Goal</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProgressChart;
