import React from 'react';
import { Lightbulb, AlertTriangle, Info, CheckCircle } from 'lucide-react';

interface Insight {
  type: 'tip' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
}

interface InsightsCardProps {
  insights: Insight[];
}

const InsightsCard: React.FC<InsightsCardProps> = ({ insights }) => {
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'tip':
        return <Lightbulb className="h-5 w-5 text-yellow-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-500" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <Lightbulb className="h-5 w-5 text-gray-500" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'tip':
        return 'bg-yellow-50 border-yellow-200';
      case 'warning':
        return 'bg-red-50 border-red-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (!insights || insights.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Nutrition Insights</h3>
        </div>
        <div className="text-center text-gray-500 py-6">
          <p>No insights available yet</p>
          <p className="text-sm">Start logging your food to get personalized nutrition insights!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-4">
        <Lightbulb className="h-5 w-5 text-primary-600" />
        <h3 className="text-lg font-semibold text-gray-900">Nutrition Insights</h3>
      </div>
      
      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">
                {getInsightIcon(insight.type)}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">
                  {insight.title}
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {insight.message}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Insights are generated based on your nutrition patterns and goals
        </p>
      </div>
    </div>
  );
};

export default InsightsCard;
