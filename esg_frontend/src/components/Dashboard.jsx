import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Zap, 
  Users, 
  Target, 
  Calendar,
  BarChart3,
  PieChart as PieChartIcon,
  Leaf,
  Factory,
  Building,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6'];

export function Dashboard({ apiBaseUrl }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/dashboard/overview`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      setDashboardData(data.data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ESG Dashboard</h1>
          <p className="text-gray-600">Real-time environmental impact and sustainability metrics</p>
        </div>
        <Alert variant="destructive" className="max-w-2xl mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Unable to load dashboard data:</strong> {error}
            <br />
            <button 
              onClick={fetchDashboardData}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Click here to retry
            </button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const scopeEmissions = dashboardData?.scope_emissions || {};
  const categoryEmissions = dashboardData?.category_emissions || {};
  const monthlyTrend = dashboardData?.monthly_trend || [];
  const recentMeasurements = dashboardData?.recent_measurements || [];
  const targetsProgress = dashboardData?.targets_summary || [];

  // Calculate totals and trends
  const totalEmissions = (scopeEmissions.scope_1 || 0) + (scopeEmissions.scope_2 || 0) + (scopeEmissions.scope_3 || 0);
  const previousMonthEmissions = monthlyTrend.length >= 2 ? monthlyTrend[monthlyTrend.length - 2]?.emissions || 0 : 0;
  const currentMonthEmissions = monthlyTrend.length >= 1 ? monthlyTrend[monthlyTrend.length - 1]?.emissions || 0 : 0;
  const emissionsTrend = previousMonthEmissions > 0 ? ((currentMonthEmissions - previousMonthEmissions) / previousMonthEmissions) * 100 : 0;

  // Prepare data for charts
  const scopeData = [
    { name: 'Scope 1 (Direct)', value: scopeEmissions.scope_1 || 0, color: '#10B981', description: 'Direct emissions from owned sources' },
    { name: 'Scope 2 (Indirect)', value: scopeEmissions.scope_2 || 0, color: '#3B82F6', description: 'Indirect emissions from purchased energy' },
    { name: 'Scope 3 (Value Chain)', value: scopeEmissions.scope_3 || 0, color: '#F59E0B', description: 'Indirect emissions from value chain' },
  ].filter(item => item.value > 0);

  const categoryData = Object.entries(categoryEmissions)
    .map(([category, value]) => ({
      category: category.charAt(0).toUpperCase() + category.slice(1),
      emissions: value,
      color: COLORS[Object.keys(categoryEmissions).indexOf(category) % COLORS.length]
    }))
    .sort((a, b) => b.emissions - a.emissions);

  const trendData = monthlyTrend.map(item => ({
    month: `${item.month}`,
    emissions: item.emissions,
    target: item.target || null
  }));

  // Calculate active targets
  const activeTargets = targetsProgress.filter(target => target.status === 'active').length;
  const completedTargets = targetsProgress.filter(target => target.status === 'completed').length;

  return (
    <div className="space-y-8">
      {/* Enhanced Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <div className="p-3 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl">
            <Leaf className="h-8 w-8 text-emerald-700" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900">ESG Dashboard</h1>
            <p className="text-lg text-gray-600 mt-1">Real-time environmental impact and sustainability metrics</p>
          </div>
        </div>
        
        {/* Quick Stats Bar */}
        <div className="flex items-center justify-center gap-8 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Last updated: {new Date().toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span>{recentMeasurements.length} recent measurements</span>
          </div>
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            <span>{activeTargets} active targets</span>
          </div>
        </div>
      </div>

      {/* Enhanced Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="shadow-lg border-0 bg-gradient-to-br from-emerald-50 to-emerald-100 hover:shadow-xl transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-semibold text-emerald-800">Scope 1 Emissions</CardTitle>
            <div className="p-2 bg-emerald-200 rounded-lg">
              <Factory className="h-4 w-4 text-emerald-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-900">{(scopeEmissions.scope_1 || 0).toFixed(1)}</div>
            <p className="text-sm text-emerald-700 mt-1">kgCO2e this year</p>
            <div className="mt-2">
              <Badge className="bg-emerald-200 text-emerald-800 hover:bg-emerald-200">
                Direct emissions
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0 bg-gradient-to-br from-blue-50 to-blue-100 hover:shadow-xl transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-semibold text-blue-800">Scope 2 Emissions</CardTitle>
            <div className="p-2 bg-blue-200 rounded-lg">
              <Zap className="h-4 w-4 text-blue-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-900">{(scopeEmissions.scope_2 || 0).toFixed(1)}</div>
            <p className="text-sm text-blue-700 mt-1">kgCO2e this year</p>
            <div className="mt-2">
              <Badge className="bg-blue-200 text-blue-800 hover:bg-blue-200">
                Purchased energy
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0 bg-gradient-to-br from-amber-50 to-amber-100 hover:shadow-xl transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-semibold text-amber-800">Scope 3 Emissions</CardTitle>
            <div className="p-2 bg-amber-200 rounded-lg">
              <Users className="h-4 w-4 text-amber-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-900">{(scopeEmissions.scope_3 || 0).toFixed(1)}</div>
            <p className="text-sm text-amber-700 mt-1">kgCO2e this year</p>
            <div className="mt-2">
              <Badge className="bg-amber-200 text-amber-800 hover:bg-amber-200">
                Value chain
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0 bg-gradient-to-br from-gray-50 to-gray-100 hover:shadow-xl transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-semibold text-gray-800">Total Emissions</CardTitle>
            <div className="p-2 bg-gray-200 rounded-lg">
              <Building className="h-4 w-4 text-gray-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{totalEmissions.toFixed(1)}</div>
            <p className="text-sm text-gray-700 mt-1">kgCO2e this year</p>
            <div className="mt-2 flex items-center gap-2">
              {emissionsTrend !== 0 && (
                <div className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                  emissionsTrend > 0 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {emissionsTrend > 0 ? (
                    <ArrowUpRight className="h-3 w-3" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3" />
                  )}
                  {Math.abs(emissionsTrend).toFixed(1)}%
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Emissions by Category */}
        <Card className="shadow-lg border-0">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <BarChart3 className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Emissions by Category</CardTitle>
                <p className="text-sm text-gray-600">Breakdown of emissions by source category</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={categoryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="category" 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                  label={{ value: 'kgCO2e', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value) => [`${value.toFixed(2)} kgCO2e`, 'Emissions']}
                />
                <Bar 
                  dataKey="emissions" 
                  fill="#10B981" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Scope Breakdown */}
        <Card className="shadow-lg border-0">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <PieChartIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Emissions by Scope</CardTitle>
                <p className="text-sm text-gray-600">GHG Protocol scope distribution</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={scopeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent, value }) => 
                    `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {scopeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value, name, props) => [
                    `${value.toFixed(2)} kgCO2e`,
                    props.payload.description
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Trend and Recent Data */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Monthly Trend - Takes 2 columns */}
        <Card className="lg:col-span-2 shadow-lg border-0">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Monthly Emissions Trend</CardTitle>
                <p className="text-sm text-gray-600">Track emissions performance over time</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorEmissions" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="month" 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                  label={{ value: 'kgCO2e', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value) => [`${value.toFixed(2)} kgCO2e`, 'Emissions']}
                />
                <Area 
                  type="monotone" 
                  dataKey="emissions" 
                  stroke="#10B981" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorEmissions)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Measurements */}
        <Card className="shadow-lg border-0">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Activity className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
                <p className="text-sm text-gray-600">Latest measurements</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[300px] overflow-y-auto">
              {recentMeasurements.slice(0, 6).map((measurement, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 text-sm">{measurement.category}</p>
                    <p className="text-xs text-gray-600 flex items-center gap-1 mt-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(measurement.date).toLocaleDateString()}
                    </p>
                    {measurement.location && (
                      <p className="text-xs text-gray-500 mt-1">{measurement.location}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-emerald-700 text-sm">
                      {(measurement.calculated_emissions || 0).toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-600">kgCO2e</p>
                  </div>
                </div>
              ))}
              {recentMeasurements.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No recent measurements</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Targets Progress */}
      {targetsProgress.length > 0 && (
        <Card className="shadow-lg border-0">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Target className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg font-semibold">ESG Targets Progress</CardTitle>
                  <p className="text-sm text-gray-600">Track progress towards sustainability goals</p>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600">{activeTargets} Active</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-600">{completedTargets} Completed</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {targetsProgress.map((target, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-xl bg-gradient-to-br from-white to-gray-50 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900 text-sm">{target.name}</h4>
                    <div className="flex items-center gap-2">
                      {target.status === 'active' ? (
                        <Clock className="h-4 w-4 text-amber-500" />
                      ) : target.status === 'completed' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                      <Badge 
                        variant={target.status === 'active' ? 'default' : 'secondary'}
                        className={
                          target.status === 'active' 
                            ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100' 
                            : target.status === 'completed'
                            ? 'bg-green-100 text-green-800 hover:bg-green-100'
                            : 'bg-gray-100 text-gray-800 hover:bg-gray-100'
                        }
                      >
                        {target.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-300 ${
                        target.status === 'completed' 
                          ? 'bg-green-500' 
                          : target.progress_percentage >= 75
                          ? 'bg-emerald-500'
                          : target.progress_percentage >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(target.progress_percentage || 0, 100)}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-900">
                      {(target.progress_percentage || 0).toFixed(1)}% complete
                    </span>
                    <span className="text-gray-600">
                      Target: {target.target_year}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

