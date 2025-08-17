import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Target, Plus, Edit, Trash2, TrendingUp, Activity, Scale, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface NutritionGoal {
  id: string;
  name: string;
  calories_goal: number;
  protein_goal_g: number;
  carbs_goal_g: number;
  fat_goal_g: number;
  fiber_goal_g: number;
  sugar_goal_g: number;
  sodium_goal_mg: number;
  weight_goal_kg?: number;
  is_active: boolean;
  created_at: string;
}

interface GoalFormData {
  name: string;
  calories_goal: number;
  protein_goal_g: number;
  carbs_goal_g: number;
  fat_goal_g: number;
  fiber_goal_g: number;
  sugar_goal_g: number;
  sodium_goal_mg: number;
  weight_goal_kg?: number;
}

const Goals: React.FC = () => {
  const [goals, setGoals] = useState<NutritionGoal[]>([
    {
      id: '1',
      name: 'Weight Loss',
      calories_goal: 1800,
      protein_goal_g: 150,
      carbs_goal_g: 150,
      fat_goal_g: 60,
      fiber_goal_g: 25,
      sugar_goal_g: 50,
      sodium_goal_mg: 2300,
      weight_goal_kg: 70,
      is_active: true,
      created_at: '2024-01-01',
    },
    {
      id: '2',
      name: 'Muscle Building',
      calories_goal: 2500,
      protein_goal_g: 200,
      carbs_goal_g: 250,
      fat_goal_g: 80,
      fiber_goal_g: 30,
      sugar_goal_g: 60,
      sodium_goal_mg: 2500,
      weight_goal_kg: 80,
      is_active: false,
      created_at: '2024-01-15',
    },
  ]);
  const [isCreating, setIsCreating] = useState(false);
  const [editingGoal, setEditingGoal] = useState<NutritionGoal | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<GoalFormData>();

  const handleCreateGoal = async (data: GoalFormData) => {
    setIsLoading(true);
    try {
      // TODO: Implement API call to create goal
      const newGoal: NutritionGoal = {
        id: Date.now().toString(),
        ...data,
        is_active: false,
        created_at: new Date().toISOString().split('T')[0],
      };
      
      setGoals([...goals, newGoal]);
      toast.success('Goal created successfully!');
      setIsCreating(false);
      reset();
    } catch (error) {
      toast.error('Failed to create goal');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateGoal = async (data: GoalFormData) => {
    if (!editingGoal) return;

    setIsLoading(true);
    try {
      // TODO: Implement API call to update goal
      const updatedGoals = goals.map(goal =>
        goal.id === editingGoal.id ? { ...goal, ...data } : goal
      );
      setGoals(updatedGoals);
      toast.success('Goal updated successfully!');
      setEditingGoal(null);
      reset();
    } catch (error) {
      toast.error('Failed to update goal');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) return;

    try {
      // TODO: Implement API call to delete goal
      const updatedGoals = goals.filter(goal => goal.id !== goalId);
      setGoals(updatedGoals);
      toast.success('Goal deleted successfully!');
    } catch (error) {
      toast.error('Failed to delete goal');
    }
  };

  const handleActivateGoal = async (goalId: string) => {
    try {
      // TODO: Implement API call to activate goal
      const updatedGoals = goals.map(goal => ({
        ...goal,
        is_active: goal.id === goalId,
      }));
      setGoals(updatedGoals);
      toast.success('Goal activated successfully!');
    } catch (error) {
      toast.error('Failed to activate goal');
    }
  };

  const openCreateForm = () => {
    setIsCreating(true);
    setEditingGoal(null);
    reset();
  };

  const openEditForm = (goal: NutritionGoal) => {
    setEditingGoal(goal);
    setIsCreating(false);
    reset({
      name: goal.name,
      calories_goal: goal.calories_goal,
      protein_goal_g: goal.protein_goal_g,
      carbs_goal_g: goal.carbs_goal_g,
      fat_goal_g: goal.fat_goal_g,
      fiber_goal_g: goal.fiber_goal_g,
      sugar_goal_g: goal.sugar_goal_g,
      sodium_goal_mg: goal.sodium_goal_mg,
      weight_goal_kg: goal.weight_goal_kg,
    });
  };

  const closeForms = () => {
    setIsCreating(false);
    setEditingGoal(null);
    reset();
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Nutrition Goals</h1>
        <p className="text-gray-600">Set and manage your nutrition targets</p>
      </div>

      {/* Create/Edit Goal Form */}
      {(isCreating || editingGoal) && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {isCreating ? 'Create New Goal' : 'Edit Goal'}
            </h3>
            <button
              onClick={closeForms}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit(isCreating ? handleCreateGoal : handleUpdateGoal)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Goal Name
                </label>
                <input
                  id="name"
                  type="text"
                  {...register('name', { required: 'Goal name is required' })}
                  className={`input-field ${errors.name ? 'border-red-300 focus:ring-red-500' : ''}`}
                  placeholder="e.g., Weight Loss, Muscle Building"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="weight_goal_kg" className="block text-sm font-medium text-gray-700 mb-2">
                  <Scale className="inline-block w-4 h-4 mr-1" />
                  Target Weight (kg)
                </label>
                <input
                  id="weight_goal_kg"
                  type="number"
                  step="0.1"
                  {...register('weight_goal_kg', { min: 20, max: 300 })}
                  className="input-field"
                  placeholder="Optional"
                />
              </div>
            </div>

            <div>
              <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Daily Nutrition Targets
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label htmlFor="calories_goal" className="block text-sm font-medium text-gray-700 mb-2">
                    <TrendingUp className="inline-block w-4 h-4 mr-1" />
                    Calories
                  </label>
                  <input
                    id="calories_goal"
                    type="number"
                    {...register('calories_goal', { 
                      required: 'Calories goal is required',
                      min: { value: 800, message: 'Minimum 800 calories' },
                      max: { value: 5000, message: 'Maximum 5000 calories' }
                    })}
                    className={`input-field ${errors.calories_goal ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.calories_goal && (
                    <p className="mt-1 text-sm text-red-600">{errors.calories_goal.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="protein_goal_g" className="block text-sm font-medium text-gray-700 mb-2">
                    Protein (g)
                  </label>
                  <input
                    id="protein_goal_g"
                    type="number"
                    {...register('protein_goal_g', { 
                      required: 'Protein goal is required',
                      min: { value: 20, message: 'Minimum 20g protein' },
                      max: { value: 500, message: 'Maximum 500g protein' }
                    })}
                    className={`input-field ${errors.protein_goal_g ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.protein_goal_g && (
                    <p className="mt-1 text-sm text-red-600">{errors.protein_goal_g.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="carbs_goal_g" className="block text-sm font-medium text-gray-700 mb-2">
                    Carbs (g)
                  </label>
                  <input
                    id="carbs_goal_g"
                    type="number"
                    {...register('carbs_goal_g', { 
                      required: 'Carbs goal is required',
                      min: { value: 20, message: 'Minimum 20g carbs' },
                      max: { value: 1000, message: 'Maximum 1000g carbs' }
                    })}
                    className={`input-field ${errors.carbs_goal_g ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.carbs_goal_g && (
                    <p className="mt-1 text-sm text-red-600">{errors.carbs_goal_g.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="fat_goal_g" className="block text-sm font-medium text-gray-700 mb-2">
                    Fat (g)
                  </label>
                  <input
                    id="fat_goal_g"
                    type="number"
                    {...register('fat_goal_g', { 
                      required: 'Fat goal is required',
                      min: { value: 20, message: 'Minimum 20g fat' },
                      max: { value: 200, message: 'Maximum 200g fat' }
                    })}
                    className={`input-field ${errors.fat_goal_g ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.fat_goal_g && (
                    <p className="mt-1 text-sm text-red-600">{errors.fat_goal_g.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="fiber_goal_g" className="block text-sm font-medium text-gray-700 mb-2">
                    Fiber (g)
                  </label>
                  <input
                    id="fiber_goal_g"
                    type="number"
                    {...register('fiber_goal_g', { 
                      required: 'Fiber goal is required',
                      min: { value: 10, message: 'Minimum 10g fiber' },
                      max: { value: 100, message: 'Maximum 100g fiber' }
                    })}
                    className={`input-field ${errors.fiber_goal_g ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.fiber_goal_g && (
                    <p className="mt-1 text-sm text-red-600">{errors.fiber_goal_g.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="sugar_goal_g" className="block text-sm font-medium text-gray-700 mb-2">
                    Sugar (g)
                  </label>
                  <input
                    id="sugar_goal_g"
                    type="number"
                    {...register('sugar_goal_g', { 
                      required: 'Sugar goal is required',
                      min: { value: 0, message: 'Minimum 0g sugar' },
                      max: { value: 200, message: 'Maximum 200g sugar' }
                    })}
                    className={`input-field ${errors.sugar_goal_g ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.sugar_goal_g && (
                    <p className="mt-1 text-sm text-red-600">{errors.sugar_goal_g.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="sodium_goal_mg" className="block text-sm font-medium text-gray-700 mb-2">
                    Sodium (mg)
                  </label>
                  <input
                    id="sodium_goal_mg"
                    type="number"
                    {...register('sodium_goal_mg', { 
                      required: 'Sodium goal is required',
                      min: { value: 500, message: 'Minimum 500mg sodium' },
                      max: { value: 5000, message: 'Maximum 5000mg sodium' }
                    })}
                    className={`input-field ${errors.sodium_goal_mg ? 'border-red-300 focus:ring-red-500' : ''}`}
                  />
                  {errors.sodium_goal_mg && (
                    <p className="mt-1 text-sm text-red-600">{errors.sodium_goal_mg.message}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={closeForms}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary"
              >
                {isLoading ? 'Saving...' : (isCreating ? 'Create Goal' : 'Update Goal')}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Goals List */}
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">Your Goals</h2>
          {!isCreating && !editingGoal && (
            <button
              onClick={openCreateForm}
              className="btn-primary"
            >
              <Plus className="inline-block w-4 h-4 mr-2" />
              Create New Goal
            </button>
          )}
        </div>

        {goals.length === 0 ? (
          <div className="card text-center py-12">
            <Target className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No goals yet</h3>
            <p className="text-gray-600 mb-4">Create your first nutrition goal to get started</p>
            <button
              onClick={openCreateForm}
              className="btn-primary"
            >
              <Plus className="inline-block w-4 h-4 mr-2" />
              Create Your First Goal
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {goals.map((goal) => (
              <div
                key={goal.id}
                className={`card ${goal.is_active ? 'ring-2 ring-primary-500' : ''}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{goal.name}</h3>
                    <p className="text-sm text-gray-500">Created {goal.created_at}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {goal.is_active && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                    <button
                      onClick={() => openEditForm(goal)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteGoal(goal.id)}
                      className="text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Goal Details */}
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Calories:</span>
                      <span className="ml-2 font-medium">{goal.calories_goal}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Protein:</span>
                      <span className="ml-2 font-medium">{goal.protein_goal_g}g</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Carbs:</span>
                      <span className="ml-2 font-medium">{goal.carbs_goal_g}g</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Fat:</span>
                      <span className="ml-2 font-medium">{goal.fat_goal_g}g</span>
                    </div>
                  </div>

                  {goal.weight_goal_kg && (
                    <div className="pt-3 border-t border-gray-200">
                      <span className="text-gray-500">Target Weight:</span>
                      <span className="ml-2 font-medium">{goal.weight_goal_kg} kg</span>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="pt-3 border-t border-gray-200">
                    {!goal.is_active ? (
                      <button
                        onClick={() => handleActivateGoal(goal.id)}
                        className="btn-primary w-full"
                      >
                        <Activity className="inline-block w-4 h-4 mr-2" />
                        Activate Goal
                      </button>
                    ) : (
                      <div className="text-center text-sm text-green-600 font-medium">
                        ✓ This is your active goal
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Goals;
