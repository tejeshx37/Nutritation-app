import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Search, Plus, MessageSquare, Calendar, Clock, Utensils } from 'lucide-react';
import toast from 'react-hot-toast';

interface FoodLogFormData {
  naturalLanguage: string;
  foodName: string;
  quantity: number;
  unit: string;
  mealType: string;
  date: string;
  time: string;
}

interface FoodItem {
  id: string;
  name: string;
  calories_per_100g: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  sodium_mg: number;
}

const FoodLog: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'natural' | 'manual'>('natural');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<FoodItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedFood, setSelectedFood] = useState<FoodItem | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FoodLogFormData>();

  // Set default values
  React.useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    const now = new Date().toTimeString().slice(0, 5);
    reset({
      date: today,
      time: now,
      mealType: 'breakfast',
      unit: 'g',
      quantity: 100,
    });
  }, [reset]);

  const handleNaturalLanguageSubmit = async (data: FoodLogFormData) => {
    try {
      // TODO: Implement natural language parsing API call
      toast.success('Food logged successfully!');
      reset();
    } catch (error) {
      toast.error('Failed to log food');
    }
  };

  const handleManualSubmit = async (data: FoodLogFormData) => {
    if (!selectedFood) {
      toast.error('Please select a food item');
      return;
    }

    try {
      // TODO: Implement manual food logging API call
      toast.success('Food logged successfully!');
      reset();
      setSelectedFood(null);
    } catch (error) {
      toast.error('Failed to log food');
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      // TODO: Implement food search API call
      // For now, show mock results
      const mockResults: FoodItem[] = [
        {
          id: '1',
          name: 'Chicken Breast',
          calories_per_100g: 165,
          protein_g: 31,
          carbs_g: 0,
          fat_g: 3.6,
          fiber_g: 0,
          sugar_g: 0,
          sodium_mg: 74,
        },
        {
          id: '2',
          name: 'Brown Rice',
          calories_per_100g: 111,
          protein_g: 2.6,
          carbs_g: 23,
          fat_g: 0.9,
          fiber_g: 1.8,
          sugar_g: 0.4,
          sodium_mg: 5,
        },
      ];
      setSearchResults(mockResults);
    } catch (error) {
      toast.error('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Food Log</h1>
        <p className="text-gray-600">Track your daily nutrition intake</p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('natural')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'natural'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <MessageSquare className="inline-block w-4 h-4 mr-2" />
              Natural Language
            </button>
            <button
              onClick={() => setActiveTab('manual')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'manual'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Plus className="inline-block w-4 h-4 mr-2" />
              Manual Entry
            </button>
          </nav>
        </div>
      </div>

      {/* Natural Language Tab */}
      {activeTab === 'natural' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <MessageSquare className="inline-block w-4 h-4 mr-2" />
              Log Food in Natural Language
            </h3>
            <p className="text-gray-600 mb-4">
              Describe what you ate in plain English. For example: "2 slices of whole wheat bread with 1 tablespoon of peanut butter"
            </p>
            
            <form onSubmit={handleSubmit(handleNaturalLanguageSubmit)} className="space-y-4">
              <div>
                <label htmlFor="naturalLanguage" className="block text-sm font-medium text-gray-700 mb-2">
                  What did you eat?
                </label>
                <textarea
                  id="naturalLanguage"
                  rows={3}
                  {...register('naturalLanguage', { required: 'Please describe what you ate' })}
                  className={`w-full input-field ${
                    errors.naturalLanguage ? 'border-red-300 focus:ring-red-500' : ''
                  }`}
                  placeholder="e.g., 2 slices of whole wheat bread with 1 tablespoon of peanut butter"
                />
                {errors.naturalLanguage && (
                  <p className="mt-1 text-sm text-red-600">{errors.naturalLanguage.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="inline-block w-4 h-4 mr-1" />
                    Date
                  </label>
                  <input
                    id="date"
                    type="date"
                    {...register('date', { required: 'Date is required' })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                    <Clock className="inline-block w-4 h-4 mr-1" />
                    Time
                  </label>
                  <input
                    id="time"
                    type="time"
                    {...register('time', { required: 'Time is required' })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label htmlFor="mealType" className="block text-sm font-medium text-gray-700 mb-2">
                    <Utensils className="inline-block w-4 h-4 mr-1" />
                    Meal Type
                  </label>
                  <select
                    id="mealType"
                    {...register('mealType', { required: 'Meal type is required' })}
                    className="input-field"
                  >
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="btn-primary w-full"
              >
                Log Food
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Manual Entry Tab */}
      {activeTab === 'manual' && (
        <div className="space-y-6">
          {/* Food Search */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <Search className="inline-block w-4 h-4 mr-2" />
              Search for Food
            </h3>
            
            <div className="space-y-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for food items..."
                  className="flex-1 input-field"
                />
                <button
                  onClick={() => handleSearch(searchQuery)}
                  disabled={isSearching}
                  className="btn-primary px-6"
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Search Results:</h4>
                  {searchResults.map((food) => (
                    <div
                      key={food.id}
                      onClick={() => setSelectedFood(food)}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedFood?.id === food.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-medium text-gray-900">{food.name}</h5>
                          <p className="text-sm text-gray-600">
                            {food.calories_per_100g} cal, {food.protein_g}g protein, {food.carbs_g}g carbs, {food.fat_g}g fat
                          </p>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          per 100g
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Manual Entry Form */}
          {selectedFood && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                <Plus className="inline-block w-4 h-4 mr-2" />
                Log {selectedFood.name}
              </h3>
              
              <form onSubmit={handleSubmit(handleManualSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity
                    </label>
                    <input
                      id="quantity"
                      type="number"
                      step="0.1"
                      {...register('quantity', { 
                        required: 'Quantity is required',
                        min: { value: 0.1, message: 'Quantity must be positive' }
                      })}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label htmlFor="unit" className="block text-sm font-medium text-gray-700 mb-2">
                      Unit
                    </label>
                    <select
                      id="unit"
                      {...register('unit', { required: 'Unit is required' })}
                      className="input-field"
                    >
                      <option value="g">grams (g)</option>
                      <option value="oz">ounces (oz)</option>
                      <option value="cup">cups</option>
                      <option value="tbsp">tablespoons (tbsp)</option>
                      <option value="tsp">teaspoons (tsp)</option>
                      <option value="piece">pieces</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="mealType" className="block text-sm font-medium text-gray-700 mb-2">
                      Meal Type
                    </label>
                    <select
                      id="mealType"
                      {...register('mealType', { required: 'Meal type is required' })}
                      className="input-field"
                    >
                      <option value="breakfast">Breakfast</option>
                      <option value="lunch">Lunch</option>
                      <option value="dinner">Dinner</option>
                      <option value="snack">Snack</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                      Date
                    </label>
                    <input
                      id="date"
                      type="date"
                      {...register('date', { required: 'Date is required' })}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                      Time
                    </label>
                    <input
                      id="time"
                      type="time"
                      {...register('time', { required: 'Time is required' })}
                      className="input-field"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-primary w-full"
                >
                  Log Food
                </button>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FoodLog;
