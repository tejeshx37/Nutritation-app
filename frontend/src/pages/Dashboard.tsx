import React from 'react';
// import { useQuery } from 'react-query';
import { dashboardAPI } from '../services/api';
import { 
  TrendingUp, 
  Target, 
  Utensils, 
  Activity,
  Calendar,
  BarChart3,
  Lightbulb
} from 'lucide-react';
import { format } from 'date-fns';
import NutritionSummaryCard from '../components/NutritionSummaryCard';
import ProgressChart from '../components/ProgressChart';
import InsightsCard from '../components/InsightsCard';

const Dashboard: React.FC = () => {
  const today = format(new Date(), 'yyyy-MM-dd');

  // Fetch today's nutrition summary
  // const { data: todaySummary, isLoading: summaryLoading } = useQuery(
  //   ['todaySummary'],
  //   dashboardAPI.getTodaySummary,
  //   {
  //     refetchInterval: 300000, // Refetch every 5 minutes
  //   }
  // );

  // Fetch progress data for charts
  // const { data: progressData, isLoading: progressLoading } = useQuery(
  //   ['progressData', 7],
  //   () => dashboardAPI.getProgressData(7),
  //   {
  //     refetchInterval: 600000, // Refetch every 10 minutes
  //   }
  // );

  // Fetch insights
  // const { data: insights, isLoading: insightsLoading } = useQuery(
  //   ['insights'],
  //     dashboardAPI.getInsights,
  //   {
  //     refetchInterval: 1800000, // Refetch every 30 minutes
  //   }
  // );

  // const isLoading = summaryLoading || progressLoading || insightsLoading;
  const isLoading = false;
  const todaySummary = {
    total_calories: 0,
    calories_goal: 2000,
    total_protein_g: 0,
    protein_goal_g: 150,
    total_carbs_g: 0,
    carbs_goal_g: 200,
    total_fat_g: 0,
    fat_goal_g: 65,
    total_meals: 0,
    total_snacks: 0,
    total_fiber_g: 0,
    total_sugar_g: 0,
    total_sodium_mg: 0
  };
  const progressData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    calories: [0, 0, 0, 0, 0, 0, 0],
    protein: [0, 0, 0, 0, 0, 0, 0],
    carbs: [0, 0, 0, 0, 0, 0, 0],
    fat: [0, 0, 0, 0, 0, 0, 0],
    calories_goal: [2000, 2000, 2000, 2000, 2000, 2000, 2000],
    protein_goal: [150, 150, 150, 150, 150, 150, 150],
    carbs_goal: [200, 200, 200, 200, 200, 200, 200],
    fat_goal: [65, 65, 65, 65, 65, 65, 65]
  };
  const insights = [
    {
      type: 'tip' as const,
      title: 'Welcome to your nutrition dashboard!',
      message: 'Start logging your food to see personalized insights and track your progress.'
    }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Welcome back! Here's your nutrition overview for {format(new Date(), 'MMMM d, yyyy')}
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Calendar className="h-4 w-4" />
          <span>{format(new Date(), 'EEEE, MMMM d')}</span>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="nutrition-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-nutrition-calories rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Calories</p>
              <p className="text-2xl font-bold text-gray-900">
                {todaySummary?.total_calories?.toFixed(0) || '0'}
              </p>
              {todaySummary?.calories_goal && (
                <p className="text-sm text-gray-500">
                  of {todaySummary.calories_goal} goal
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="nutrition-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-nutrition-protein rounded-lg flex items-center justify-center">
                <Target className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Protein</p>
              <p className="text-2xl font-bold text-gray-900">
                {todaySummary?.total_protein_g?.toFixed(1) || '0'}g
              </p>
              {todaySummary?.protein_goal_g && (
                <p className="text-sm text-gray-500">
                  of {todaySummary.protein_goal_g}g goal
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="nutrition-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-nutrition-carbs rounded-lg flex items-center justify-center">
                <Utensils className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Carbs</p>
              <p className="text-2xl font-bold text-gray-900">
                {todaySummary?.total_carbs_g?.toFixed(1) || '0'}g
              </p>
              {todaySummary?.carbs_goal_g && (
                <p className="text-sm text-gray-500">
                  of {todaySummary.carbs_goal_g}g goal
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="nutrition-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-nutrition-fat rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Fat</p>
              <p className="text-2xl font-bold text-gray-900">
                {todaySummary?.total_fat_g?.toFixed(1) || '0'}g
              </p>
              {todaySummary?.fat_goal_g && (
                <p className="text-sm text-gray-500">
                  of {todaySummary.fat_goal_g}g goal
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Nutrition Summary */}
        <div className="lg:col-span-2">
          <NutritionSummaryCard summary={todaySummary} />
        </div>

        {/* Insights */}
        <div className="space-y-6">
          <InsightsCard insights={insights || []} />
          
          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary">
                Log Food
              </button>
              <button className="w-full btn-secondary">
                Set Goals
              </button>
              <button className="w-full btn-secondary">
                View Progress
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Charts */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Weekly Progress</h3>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <BarChart3 className="h-4 w-4" />
            <span>Last 7 days</span>
          </div>
        </div>
        
        {progressData && (
          <ProgressChart data={progressData} />
        )}
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Meals Today</h4>
          <p className="text-2xl font-bold text-gray-900">
            {todaySummary?.total_meals || 0}
          </p>
          <p className="text-sm text-gray-500">main meals</p>
        </div>

        <div className="card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Snacks</h4>
          <p className="text-2xl font-bold text-gray-900">
            {todaySummary?.total_snacks || 0}
          </p>
          <p className="text-sm text-gray-500">snacks consumed</p>
        </div>

        <div className="card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Fiber</h4>
          <p className="text-2xl font-bold text-gray-900">
            {todaySummary?.total_fiber_g?.toFixed(1) || '0'}g
          </p>
          <p className="text-sm text-gray-500">dietary fiber</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
