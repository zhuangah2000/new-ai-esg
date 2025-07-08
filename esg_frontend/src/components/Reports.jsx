import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Area, AreaChart } from 'recharts';
import { Download, FileText, BarChart3, Target, FolderOpen, Users, TrendingUp, AlertCircle, CheckCircle, Clock, Info, Globe, Building, Leaf, Shield } from 'lucide-react';

const Reports = () => {
  const [selectedYear, setSelectedYear] = useState(2025);
  const [selectedFramework, setSelectedFramework] = useState('gri');
  const [loading, setLoading] = useState(true);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [frameworks, setFrameworks] = useState({});
  
  // Data states
  const [comprehensiveData, setComprehensiveData] = useState(null);
  const [emissionsData, setEmissionsData] = useState(null);
  const [targetsData, setTargetsData] = useState(null);
  const [projectsData, setProjectsData] = useState(null);
  const [suppliersData, setSuppliersData] = useState(null);

  // Enhanced color schemes for different frameworks
  const FRAMEWORK_COLORS = {
    gri: ['#2E8B57', '#32CD32', '#90EE90', '#98FB98', '#F0FFF0'],
    sasb: ['#4169E1', '#6495ED', '#87CEEB', '#B0E0E6', '#F0F8FF'],
    tcfd: ['#FF6347', '#FF7F50', '#FFA07A', '#FFB6C1', '#FFF0F5'],
    cdp: ['#008B8B', '#20B2AA', '#48D1CC', '#AFEEEE', '#F0FFFF'],
    ifrs: ['#9932CC', '#BA55D3', '#DA70D6', '#DDA0DD', '#F8F0FF']
  };

  const COLORS = FRAMEWORK_COLORS[selectedFramework] || FRAMEWORK_COLORS.gri;

  useEffect(() => {
    fetchFrameworks();
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [selectedYear, selectedFramework]);

  const fetchFrameworks = async () => {
    try {
      const response = await fetch('/api/reports/frameworks');
      if (response.ok) {
        const data = await response.json();
        setFrameworks(data.frameworks);
      }
    } catch (error) {
      console.error('Error fetching frameworks:', error);
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchComprehensiveData(),
        fetchEmissionsData(),
        fetchTargetsData(),
        fetchProjectsData(),
        fetchSuppliersData()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchComprehensiveData = async () => {
    try {
      const response = await fetch(`/api/reports/comprehensive?year=${selectedYear}&framework=${selectedFramework}`);
      if (response.ok) {
        const data = await response.json();
        setComprehensiveData(data);
      } else {
        setComprehensiveData(null);
      }
    } catch (error) {
      console.error('Error fetching comprehensive data:', error);
      setComprehensiveData(null);
    }
  };

  const fetchEmissionsData = async () => {
    try {
      const response = await fetch(`/api/reports/emissions?year=${selectedYear}`);
      if (response.ok) {
        const data = await response.json();
        setEmissionsData(data);
      } else {
        setEmissionsData(null);
      }
    } catch (error) {
      console.error('Error fetching emissions data:', error);
      setEmissionsData(null);
    }
  };

  const fetchTargetsData = async () => {
    try {
      const response = await fetch(`/api/reports/targets?year=${selectedYear}`);
      if (response.ok) {
        const data = await response.json();
        setTargetsData(data);
      } else {
        setTargetsData(null);
      }
    } catch (error) {
      console.error('Error fetching targets data:', error);
      setTargetsData(null);
    }
  };

  const fetchProjectsData = async () => {
    try {
      const response = await fetch(`/api/reports/projects?year=${selectedYear}`);
      if (response.ok) {
        const data = await response.json();
        setProjectsData(data);
      } else {
        setProjectsData(null);
      }
    } catch (error) {
      console.error('Error fetching projects data:', error);
      setProjectsData(null);
    }
  };

  const fetchSuppliersData = async () => {
    try {
      const response = await fetch(`/api/reports/suppliers?year=${selectedYear}`);
      if (response.ok) {
        const data = await response.json();
        setSuppliersData(data);
      } else {
        setSuppliersData(null);
      }
    } catch (error) {
      console.error('Error fetching suppliers data:', error);
      setSuppliersData(null);
    }
  };

  const handleExport = async (type, format) => {
    try {
      const response = await fetch(`/api/reports/export/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: type,
          year: selectedYear,
          framework: selectedFramework
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `ESG_${type.charAt(0).toUpperCase() + type.slice(1)}_Report_${selectedFramework.toUpperCase()}_${selectedYear}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setExportDialogOpen(false);
      } else {
        console.error('Export failed:', response.status);
      }
    } catch (error) {
      console.error('Error exporting report:', error);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'on-track': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'at-risk': { color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle },
      'behind': { color: 'bg-red-100 text-red-800', icon: AlertCircle },
      'active': { color: 'bg-blue-100 text-blue-800', icon: Clock },
      'completed': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'on_hold': { color: 'bg-gray-100 text-gray-800', icon: Clock },
      'cancelled': { color: 'bg-red-100 text-red-800', icon: AlertCircle }
    };

    const config = statusConfig[status] || statusConfig['active'];
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
      </Badge>
    );
  };

  const getFrameworkIcon = (framework) => {
    const icons = {
      gri: Globe,
      sasb: Building,
      tcfd: TrendingUp,
      cdp: Leaf,
      ifrs: Shield
    };
    return icons[framework] || Globe;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading reports...</div>
      </div>
    );
  }

  const currentFramework = frameworks[selectedFramework] || {};

  return (
    <div className="space-y-6">
      {/* Enhanced Header with Framework Selection */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg border">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">ESG Sustainability Reports</h1>
            <p className="text-gray-600 mt-2">Comprehensive ESG performance analytics and reporting</p>
            
            {/* Framework Information */}
            {currentFramework.name && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  {React.createElement(getFrameworkIcon(selectedFramework), { className: "w-5 h-5 text-blue-600" })}
                  <h3 className="font-semibold text-lg">{currentFramework.name}</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">{currentFramework.description}</p>
                <div className="flex items-center gap-2">
                  <Info className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-medium text-blue-700">Focus: {currentFramework.focus}</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            {/* Framework Selector */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700">Reporting Framework</label>
              <Select value={selectedFramework} onValueChange={setSelectedFramework}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select Framework" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gri">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4" />
                      GRI Standards
                    </div>
                  </SelectItem>
                  <SelectItem value="sasb">
                    <div className="flex items-center gap-2">
                      <Building className="w-4 h-4" />
                      SASB Standards
                    </div>
                  </SelectItem>
                  <SelectItem value="tcfd">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      TCFD Framework
                    </div>
                  </SelectItem>
                  <SelectItem value="cdp">
                    <div className="flex items-center gap-2">
                      <Leaf className="w-4 h-4" />
                      CDP Disclosure
                    </div>
                  </SelectItem>
                  <SelectItem value="ifrs">
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      IFRS Standards
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Year Selector */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700">Reporting Year</label>
              <Select value={selectedYear.toString()} onValueChange={(value) => setSelectedYear(parseInt(value))}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Year" />
                </SelectTrigger>
                <SelectContent>
                  {[2025, 2024, 2023, 2022, 2021, 2020].map(year => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {/* Export Button */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700 opacity-0">Export</label>
              <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700">
                    <Download className="w-4 h-4 mr-2" />
                    Export Report
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Export ESG Report ({currentFramework.name || 'GRI'})</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        Reports will be generated according to {currentFramework.name || 'GRI Standards'} framework requirements.
                      </AlertDescription>
                    </Alert>
                    
                    <div className="grid grid-cols-1 gap-3">
                      <Button 
                        onClick={() => handleExport('comprehensive', 'pdf')}
                        className="justify-start bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Comprehensive Report (PDF)
                      </Button>
                      <Button 
                        onClick={() => handleExport('emissions', 'pdf')}
                        variant="outline"
                        className="justify-start border-green-300 hover:bg-green-50"
                      >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        Emissions Report (PDF)
                      </Button>
                      <Button 
                        onClick={() => handleExport('targets', 'pdf')}
                        variant="outline"
                        className="justify-start border-blue-300 hover:bg-blue-50"
                      >
                        <Target className="w-4 h-4 mr-2" />
                        Targets Report (PDF)
                      </Button>
                      <Button 
                        onClick={() => handleExport('projects', 'pdf')}
                        variant="outline"
                        className="justify-start border-purple-300 hover:bg-purple-50"
                      >
                        <FolderOpen className="w-4 h-4 mr-2" />
                        Projects Report (PDF)
                      </Button>
                      <Button 
                        onClick={() => handleExport('suppliers', 'pdf')}
                        variant="outline"
                        className="justify-start border-orange-300 hover:bg-orange-50"
                      >
                        <Users className="w-4 h-4 mr-2" />
                        Suppliers Report (PDF)
                      </Button>
                    </div>
                    
                    <div className="border-t pt-4">
                      <p className="text-sm text-gray-600 mb-3">CSV Data Export:</p>
                      <div className="grid grid-cols-2 gap-2">
                        <Button 
                          onClick={() => handleExport('emissions', 'csv')}
                          variant="outline"
                          size="sm"
                          className="border-green-300"
                        >
                          Emissions CSV
                        </Button>
                        <Button 
                          onClick={() => handleExport('projects', 'csv')}
                          variant="outline"
                          size="sm"
                          className="border-purple-300"
                        >
                          Projects CSV
                        </Button>
                        <Button 
                          onClick={() => handleExport('suppliers', 'csv')}
                          variant="outline"
                          size="sm"
                          className="border-orange-300"
                        >
                          Suppliers CSV
                        </Button>
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Executive Summary Cards */}
      {comprehensiveData && comprehensiveData.summary ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700">Total Emissions</p>
                  <p className="text-3xl font-bold text-green-900">{comprehensiveData.summary.total_emissions.toLocaleString()}</p>
                  <p className="text-xs text-green-600">tCO2e</p>
                </div>
                <div className="p-3 bg-green-200 rounded-full">
                  <BarChart3 className="w-8 h-8 text-green-700" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-700">Active Targets</p>
                  <p className="text-3xl font-bold text-blue-900">{comprehensiveData.summary.active_targets}</p>
                  <p className="text-xs text-blue-600">ESG targets</p>
                </div>
                <div className="p-3 bg-blue-200 rounded-full">
                  <Target className="w-8 h-8 text-blue-700" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-700">Total Projects</p>
                  <p className="text-3xl font-bold text-purple-900">{comprehensiveData.summary.total_projects}</p>
                  <p className="text-xs text-purple-600">ESG projects</p>
                </div>
                <div className="p-3 bg-purple-200 rounded-full">
                  <FolderOpen className="w-8 h-8 text-purple-700" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-700">Total Suppliers</p>
                  <p className="text-3xl font-bold text-orange-900">{comprehensiveData.summary.total_suppliers}</p>
                  <p className="text-xs text-orange-600">suppliers</p>
                </div>
                <div className="p-3 bg-orange-200 rounded-full">
                  <Users className="w-8 h-8 text-orange-700" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="p-8 text-center text-gray-500">
            <p>No executive summary data available for {selectedYear}</p>
            <p className="text-sm mt-2">Try selecting year 2024 where data exists</p>
          </CardContent>
        </Card>
      )}

      {/* Enhanced Detailed Reports Tabs */}
      <Tabs defaultValue="emissions" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5 bg-gray-100">
          <TabsTrigger value="emissions" className="data-[state=active]:bg-green-500 data-[state=active]:text-white">
            <BarChart3 className="w-4 h-4 mr-2" />
            Emissions
          </TabsTrigger>
          <TabsTrigger value="targets" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">
            <Target className="w-4 h-4 mr-2" />
            Targets
          </TabsTrigger>
          <TabsTrigger value="projects" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <FolderOpen className="w-4 h-4 mr-2" />
            Projects
          </TabsTrigger>
          <TabsTrigger value="suppliers" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white">
            <Users className="w-4 h-4 mr-2" />
            Suppliers
          </TabsTrigger>
          <TabsTrigger value="trends" className="data-[state=active]:bg-teal-500 data-[state=active]:text-white">
            <TrendingUp className="w-4 h-4 mr-2" />
            Trends
          </TabsTrigger>
        </TabsList>

        {/* Enhanced Emissions Tab */}
        <TabsContent value="emissions" className="space-y-6">
          {emissionsData ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Enhanced Scope Breakdown */}
              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <BarChart3 className="w-5 h-5" />
                    Emissions by Scope
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {emissionsData.scope_breakdown && emissionsData.scope_breakdown.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={emissionsData.scope_breakdown}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ scope, emissions }) => `Scope ${scope}: ${emissions.toFixed(1)} tCO2e`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="emissions"
                        >
                          {emissionsData.scope_breakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value.toFixed(2)} tCO2e`, 'Emissions']} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-gray-500">
                      No scope data available for {selectedYear}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Enhanced Category Breakdown */}
              <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-800">
                    <BarChart3 className="w-5 h-5" />
                    Emissions by Category
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {emissionsData.category_breakdown && emissionsData.category_breakdown.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={emissionsData.category_breakdown}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value.toFixed(2)} tCO2e`, 'Emissions']} />
                        <Bar dataKey="emissions" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-gray-500">
                      No category data available for {selectedYear}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Enhanced Detailed Breakdown Table */}
              <Card className="lg:col-span-2 bg-gradient-to-br from-gray-50 to-slate-50 border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <FileText className="w-5 h-5" />
                    Detailed Emissions Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {emissionsData.category_breakdown && emissionsData.category_breakdown.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse border border-gray-300 rounded-lg overflow-hidden">
                        <thead>
                          <tr className="bg-gradient-to-r from-gray-100 to-gray-200">
                            <th className="border border-gray-300 px-4 py-3 text-left font-semibold">Category</th>
                            <th className="border border-gray-300 px-4 py-3 text-right font-semibold">Emissions (tCO2e)</th>
                            <th className="border border-gray-300 px-4 py-3 text-right font-semibold">Measurements</th>
                            <th className="border border-gray-300 px-4 py-3 text-right font-semibold">Percentage</th>
                          </tr>
                        </thead>
                        <tbody>
                          {emissionsData.category_breakdown.map((item, index) => {
                            const totalEmissions = emissionsData.category_breakdown.reduce((sum, cat) => sum + cat.emissions, 0);
                            const percentage = totalEmissions > 0 ? (item.emissions / totalEmissions * 100) : 0;
                            return (
                              <tr key={index} className="hover:bg-gray-50 transition-colors">
                                <td className="border border-gray-300 px-4 py-3 font-medium">{item.category}</td>
                                <td className="border border-gray-300 px-4 py-3 text-right">{item.emissions.toFixed(2)}</td>
                                <td className="border border-gray-300 px-4 py-3 text-right">{item.measurement_count}</td>
                                <td className="border border-gray-300 px-4 py-3 text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <div className="w-16 bg-gray-200 rounded-full h-2">
                                      <div 
                                        className="bg-green-500 h-2 rounded-full" 
                                        style={{ width: `${percentage}%` }}
                                      ></div>
                                    </div>
                                    <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No emissions data available for {selectedYear}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No emissions data available for {selectedYear}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Enhanced Targets Tab */}
        <TabsContent value="targets" className="space-y-6">
          {targetsData ? (
            <>
              {/* Enhanced Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-blue-900">{targetsData.summary?.total || 0}</p>
                      <p className="text-sm text-blue-700 font-medium">Total Targets</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-900">{targetsData.summary?.on_track || 0}</p>
                      <p className="text-sm text-green-700 font-medium">On Track</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-yellow-900">{targetsData.summary?.at_risk || 0}</p>
                      <p className="text-sm text-yellow-700 font-medium">At Risk</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-red-900">{targetsData.summary?.behind || 0}</p>
                      <p className="text-sm text-red-700 font-medium">Behind</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Targets List */}
              <Card className="bg-gradient-to-br from-slate-50 to-gray-50 border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <Target className="w-5 h-5" />
                    Target Details & Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {targetsData.targets && targetsData.targets.length > 0 ? (
                    <div className="space-y-4">
                      {targetsData.targets.map((target) => (
                        <div key={target.id} className="border rounded-lg p-6 bg-white shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg text-gray-900">{target.name}</h3>
                              <p className="text-sm text-gray-600 mt-1">{target.description}</p>
                              <div className="flex gap-2 mt-2">
                                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                  {target.category}
                                </Badge>
                              </div>
                            </div>
                            <div className="ml-4">
                              {getStatusBadge(target.status)}
                            </div>
                          </div>
                          
                          <div className="mb-4">
                            <div className="flex justify-between text-sm mb-2">
                              <span className="font-medium text-gray-700">Progress</span>
                              <span className="font-bold text-gray-900">{target.progress}%</span>
                            </div>
                            <Progress value={target.progress} className="h-3" />
                          </div>
                          
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div className="bg-gray-50 p-3 rounded-lg">
                              <p className="text-gray-600 font-medium">Baseline ({target.baseline_year})</p>
                              <p className="font-bold text-gray-900">{target.baseline_value} {target.unit}</p>
                            </div>
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <p className="text-blue-600 font-medium">Current</p>
                              <p className="font-bold text-blue-900">{target.current_value || 'N/A'} {target.unit}</p>
                            </div>
                            <div className="bg-green-50 p-3 rounded-lg">
                              <p className="text-green-600 font-medium">Target ({target.target_year})</p>
                              <p className="font-bold text-green-900">{target.target_value} {target.unit}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No targets available for {selectedYear}
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No targets data available for {selectedYear}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Enhanced Projects Tab */}
        <TabsContent value="projects" className="space-y-6">
          {projectsData ? (
            <>
              {/* Enhanced Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-purple-900">{projectsData.summary?.total || 0}</p>
                      <p className="text-sm text-purple-700 font-medium">Total Projects</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-blue-900">{projectsData.summary?.active || 0}</p>
                      <p className="text-sm text-blue-700 font-medium">Active</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-900">{projectsData.summary?.completed || 0}</p>
                      <p className="text-sm text-green-700 font-medium">Completed</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-orange-900">{projectsData.summary?.average_progress || 0}%</p>
                      <p className="text-sm text-orange-700 font-medium">Avg Progress</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Projects List */}
              <Card className="bg-gradient-to-br from-slate-50 to-gray-50 border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <FolderOpen className="w-5 h-5" />
                    Project Portfolio & Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {projectsData.projects && projectsData.projects.length > 0 ? (
                    <div className="space-y-4">
                      {projectsData.projects.map((project) => (
                        <div key={project.id} className="border rounded-lg p-6 bg-white shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg text-gray-900">{project.name}</h3>
                              <p className="text-sm text-gray-600 mt-1">{project.description}</p>
                              <div className="flex gap-2 mt-2">
                                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                  {project.category}
                                </Badge>
                                {project.target_reduction && (
                                  <Badge variant="secondary" className="bg-green-50 text-green-700 border-green-200">
                                    Target: {project.target_reduction} {project.target_reduction_unit}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <div className="ml-4">
                              {getStatusBadge(project.status)}
                            </div>
                          </div>
                          
                          <div className="mb-4">
                            <div className="flex justify-between text-sm mb-2">
                              <span className="font-medium text-gray-700">Progress</span>
                              <span className="font-bold text-gray-900">{project.progress}%</span>
                            </div>
                            <Progress value={project.progress} className="h-3" />
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <p className="text-blue-600 font-medium">Activities</p>
                              <p className="font-bold text-blue-900">{project.completed_activities}/{project.total_activities} completed</p>
                            </div>
                            <div className="bg-gray-50 p-3 rounded-lg">
                              <p className="text-gray-600 font-medium">Timeline</p>
                              <p className="font-bold text-gray-900">
                                {project.start_date ? new Date(project.start_date).toLocaleDateString() : 'N/A'} - {project.end_date ? new Date(project.end_date).toLocaleDateString() : 'Ongoing'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No projects available for {selectedYear}
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No projects data available for {selectedYear}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Enhanced Suppliers Tab */}
        <TabsContent value="suppliers" className="space-y-6">
          {suppliersData ? (
            <>
              {/* Enhanced Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-orange-900">{suppliersData.summary?.total || 0}</p>
                      <p className="text-sm text-orange-700 font-medium">Total Suppliers</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-900">{suppliersData.summary?.high_rating || 0}</p>
                      <p className="text-sm text-green-700 font-medium">High Rating (A)</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-blue-900">{suppliersData.summary?.average_compliance || 0}%</p>
                      <p className="text-sm text-blue-700 font-medium">Avg Compliance</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Suppliers List */}
              <Card className="bg-gradient-to-br from-slate-50 to-gray-50 border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <Users className="w-5 h-5" />
                    Supplier ESG Performance Assessment
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {suppliersData.suppliers && suppliersData.suppliers.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse border border-gray-300 rounded-lg overflow-hidden">
                        <thead>
                          <tr className="bg-gradient-to-r from-gray-100 to-gray-200">
                            <th className="border border-gray-300 px-4 py-3 text-left font-semibold">Supplier</th>
                            <th className="border border-gray-300 px-4 py-3 text-left font-semibold">Contact</th>
                            <th className="border border-gray-300 px-4 py-3 text-center font-semibold">Compliance Score</th>
                            <th className="border border-gray-300 px-4 py-3 text-center font-semibold">ESG Rating</th>
                            <th className="border border-gray-300 px-4 py-3 text-center font-semibold">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {suppliersData.suppliers.map((supplier) => (
                            <tr key={supplier.id} className="hover:bg-gray-50 transition-colors">
                              <td className="border border-gray-300 px-4 py-3">
                                <div>
                                  <p className="font-medium text-gray-900">{supplier.name}</p>
                                  <p className="text-sm text-gray-600">{supplier.industry}</p>
                                </div>
                              </td>
                              <td className="border border-gray-300 px-4 py-3">
                                <div>
                                  <p className="font-medium text-gray-900">{supplier.contact_person}</p>
                                  <p className="text-sm text-gray-600">{supplier.email}</p>
                                </div>
                              </td>
                              <td className="border border-gray-300 px-4 py-3 text-center">
                                <div className="flex items-center justify-center">
                                  <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                    <div 
                                      className="bg-blue-500 h-2 rounded-full" 
                                      style={{ width: `${supplier.compliance_score}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-sm font-medium">{supplier.compliance_score}%</span>
                                </div>
                              </td>
                              <td className="border border-gray-300 px-4 py-3 text-center">
                                <Badge 
                                  className={
                                    supplier.rating === 'A' ? 'bg-green-100 text-green-800' :
                                    supplier.rating === 'B' ? 'bg-yellow-100 text-yellow-800' :
                                    supplier.rating === 'C' ? 'bg-orange-100 text-orange-800' :
                                    'bg-red-100 text-red-800'
                                  }
                                >
                                  {supplier.rating}
                                </Badge>
                              </td>
                              <td className="border border-gray-300 px-4 py-3 text-center">
                                {getStatusBadge(supplier.status)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No suppliers data available
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No suppliers data available
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Enhanced Trends Tab */}
        <TabsContent value="trends" className="space-y-6">
          <Card className="bg-gradient-to-br from-teal-50 to-cyan-50 border-teal-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-teal-800">
                <TrendingUp className="w-5 h-5" />
                Monthly Emissions Trend Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {comprehensiveData && comprehensiveData.monthly_trend && comprehensiveData.monthly_trend.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={comprehensiveData.monthly_trend}>
                    <defs>
                      <linearGradient id="colorEmissions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS[0]} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={COLORS[0]} stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="month" 
                      tickFormatter={(month) => {
                        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                        return monthNames[month - 1];
                      }}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(month) => {
                        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                        return monthNames[month - 1];
                      }}
                      formatter={(value) => [`${value.toFixed(2)} tCO2e`, 'Emissions']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="emissions" 
                      stroke={COLORS[0]} 
                      fillOpacity={1} 
                      fill="url(#colorEmissions)" 
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  No trend data available for {selectedYear}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export { Reports };

