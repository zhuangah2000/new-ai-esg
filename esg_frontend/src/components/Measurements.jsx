import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Zap, 
  Fuel, 
  Droplets, 
  Trash, 
  Calendar, 
  FileText, 
  Filter, 
  Search,
  FilterX,
  TrendingUp,
  BarChart3,
  AlertCircle,
  MapPin,
  Calculator
} from 'lucide-react';

export function Measurements({ apiBaseUrl }) {
  const [measurements, setMeasurements] = useState([]);
  const [emissionFactors, setEmissionFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingMeasurement, setEditingMeasurement] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  
  // Enhanced filtering state
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');
  const [monthFilter, setMonthFilter] = useState('all');
  const [locationFilter, setLocationFilter] = useState('all');
  
  const [formData, setFormData] = useState({
    date: '',
    category: '',
    amount: '',
    unit: '',
    emission_factor_id: '',
    location: '',
    notes: ''
  });

  // Updated categories with enhanced styling and default units
  const categories = [
    { 
      id: 'electricity', 
      name: 'Electricity', 
      icon: Zap, 
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      bgGradient: 'from-yellow-50 to-yellow-100',
      defaultUnit: 'kWh'
    },
    { 
      id: 'fuel', 
      name: 'Fuel', 
      icon: Fuel, 
      color: 'bg-red-100 text-red-800 border-red-200',
      bgGradient: 'from-red-50 to-red-100',
      defaultUnit: 'L' // Liters for fuel
    },
    { 
      id: 'water', 
      name: 'Water', 
      icon: Droplets, 
      color: 'bg-blue-100 text-blue-800 border-blue-200',
      bgGradient: 'from-blue-50 to-blue-100',
      defaultUnit: 'm³' // Cubic meters for water
    },
    { 
      id: 'waste', 
      name: 'Waste', 
      icon: Trash, 
      color: 'bg-green-100 text-green-800 border-green-200',
      bgGradient: 'from-green-50 to-green-100',
      defaultUnit: 'kg' // Kilograms for waste
    }
  ];

  // Month names for display
  const months = [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' }
  ];

  useEffect(() => {
    fetchMeasurements();
    fetchEmissionFactors();
  }, []);

  const fetchMeasurements = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/measurements`);
      if (!response.ok) throw new Error('Failed to fetch measurements');
      const data = await response.json();
      console.log('Fetched measurements:', data);
      
      // Filter out measurements with transportation or assets categories
      const allowedCategories = ['electricity', 'fuel', 'water', 'waste'];
      const filteredMeasurements = (data.data || []).filter(measurement => 
        measurement.emission_factor && allowedCategories.includes(measurement.emission_factor.category)
      );
      setMeasurements(filteredMeasurements);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching measurements:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmissionFactors = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/emission-factors`);
      if (!response.ok) throw new Error('Failed to fetch emission factors');
      const data = await response.json();
      console.log('Fetched emission factors:', data);
      
      // Filter emission factors to only include the allowed categories
      const allowedCategories = ['electricity', 'fuel', 'water', 'waste'];
      const filteredFactors = (data.data || []).filter(factor => 
        allowedCategories.includes(factor.category)
      );
      setEmissionFactors(filteredFactors);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching emission factors:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Submitting form data:', formData);
      
      const url = editingMeasurement 
        ? `${apiBaseUrl}/measurements/${editingMeasurement.id}`
        : `${apiBaseUrl}/measurements`;
      
      const method = editingMeasurement ? 'PUT' : 'POST';
      
      // Prepare data with correct field names for backend
      const submitData = {
        date: formData.date,
        category: formData.category,
        amount: parseFloat(formData.amount),
        unit: formData.unit,
        emission_factor_id: parseInt(formData.emission_factor_id),
        location: formData.location,
        notes: formData.notes
      };
      
      console.log('Sending to backend:', submitData);
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save measurement');
      }
      
      await fetchMeasurements();
      setIsDialogOpen(false);
      setEditingMeasurement(null);
      resetForm();
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error submitting measurement:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      date: '',
      category: '',
      amount: '',
      unit: '',
      emission_factor_id: '',
      location: '',
      notes: ''
    });
  };

  const handleEdit = (measurement) => {
    setEditingMeasurement(measurement);
    setFormData({
      date: measurement.date,
      category: measurement.category,
      amount: measurement.amount.toString(),
      unit: measurement.unit,
      emission_factor_id: measurement.emission_factor_id.toString(),
      location: measurement.location || '',
      notes: measurement.notes || ''
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this measurement?')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/measurements/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete measurement');
      await fetchMeasurements();
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const getCategoryInfo = (category) => {
    return categories.find(cat => cat.id === category) || 
           { name: category, icon: FileText, color: 'bg-gray-100 text-gray-800 border-gray-200', bgGradient: 'from-gray-50 to-gray-100', defaultUnit: '' };
  };

  const getEmissionFactorsByCategory = (category) => {
    return emissionFactors.filter(factor => factor.category === category);
  };

  const calculateEmissions = (measurement) => {
    if (!measurement.calculated_emissions) return 0;
    return parseFloat(measurement.calculated_emissions).toFixed(2);
  };

  // Handle category change and auto-set unit
  const handleCategoryChange = (category) => {
    const categoryInfo = getCategoryInfo(category);
    setFormData({ 
      ...formData, 
      category: category, 
      emission_factor_id: '',
      unit: categoryInfo.defaultUnit || ''
    });
  };

  // Handle category tile click for filtering
  const handleCategoryTileClick = (categoryId) => {
    const currentYear = new Date().getFullYear().toString();
    setActiveTab(categoryId);
    setYearFilter(currentYear);
    // Clear other filters when clicking category tile
    setSearchTerm('');
    setMonthFilter('all');
    setLocationFilter('all');
  };

  // Enhanced filtering logic
  const getFilteredMeasurements = () => {
    let filtered = measurements;

    // Filter by category tab
    if (activeTab !== 'all') {
      filtered = filtered.filter(m => m.emission_factor && m.emission_factor.category === activeTab);
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(m => 
        m.emission_factor?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.notes?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by year
    if (yearFilter !== 'all') {
      filtered = filtered.filter(m => new Date(m.date).getFullYear().toString() === yearFilter);
    }

    // Filter by month
    if (monthFilter !== 'all') {
      filtered = filtered.filter(m => {
        const month = (new Date(m.date).getMonth() + 1).toString().padStart(2, '0');
        return month === monthFilter;
      });
    }

    // Filter by location
    if (locationFilter !== 'all') {
      filtered = filtered.filter(m => m.location === locationFilter);
    }

    return filtered;
  };

  // Get unique years and locations for filters
  const getUniqueYears = () => {
    const years = [...new Set(measurements.map(m => new Date(m.date).getFullYear()))];
    return years.sort((a, b) => b - a);
  };

  const getUniqueLocations = () => {
    const locations = [...new Set(measurements.map(m => m.location).filter(Boolean))];
    return locations.sort();
  };

  // Clear all filters
  const clearAllFilters = () => {
    setSearchTerm('');
    setYearFilter('all');
    setMonthFilter('all');
    setLocationFilter('all');
    setActiveTab('all');
  };

  const hasActiveFilters = searchTerm || yearFilter !== 'all' || monthFilter !== 'all' || locationFilter !== 'all' || activeTab !== 'all';

  // Auto-select category when changing tabs
  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    if (newTab !== 'all') {
      setFormData(prev => ({ ...prev, category: newTab }));
    }
  };

  // Calculate category summaries for current year
  const getCategorySummary = (categoryId) => {
    const currentYear = new Date().getFullYear();
    const categoryMeasurements = measurements.filter(m => 
      m.emission_factor && 
      m.emission_factor.category === categoryId &&
      new Date(m.date).getFullYear() === currentYear
    );
    
    const totalEmissions = categoryMeasurements.reduce((sum, m) => sum + (parseFloat(m.calculated_emissions) || 0), 0);
    const count = categoryMeasurements.length;
    
    return { totalEmissions: totalEmissions.toFixed(1), count };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Measurements</h1>
          <p className="text-gray-600 mt-1">Record consumption data for emissions calculations using active emission factors</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              onClick={() => {
                setEditingMeasurement(null);
                resetForm();
                // Pre-fill category if a specific tab is active
                if (activeTab !== 'all') {
                  const categoryInfo = getCategoryInfo(activeTab);
                  setFormData(prev => ({ 
                    ...prev, 
                    category: activeTab,
                    unit: categoryInfo.defaultUnit || ''
                  }));
                }
              }}
              className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Measurement
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl">
                {editingMeasurement ? (
                  <>
                    <Edit className="h-5 w-5 text-blue-600" />
                    Edit Measurement
                  </>
                ) : (
                  <>
                    <Plus className="h-5 w-5 text-emerald-600" />
                    Add New Measurement
                  </>
                )}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="date" className="text-sm font-medium text-gray-700">Measurement Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category" className="text-sm font-medium text-gray-700">Category</Label>
                  <Select 
                    value={formData.category} 
                    onValueChange={handleCategoryChange}
                    required
                  >
                    <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(category => (
                        <SelectItem key={category.id} value={category.id}>
                          <div className="flex items-center gap-2">
                            <category.icon className="h-4 w-4" />
                            {category.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location" className="text-sm font-medium text-gray-700">Location</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="Building, facility, or location"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="emission_factor_id" className="text-sm font-medium text-gray-700">Emission Factor (Active Version)</Label>
                <Select 
                  value={formData.emission_factor_id} 
                  onValueChange={(value) => setFormData({ ...formData, emission_factor_id: value })}
                  required
                >
                  <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500 h-auto min-h-[2.5rem]">
                    <SelectValue placeholder="Select emission factor" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[300px]">
                    {formData.category && getEmissionFactorsByCategory(formData.category).map(factor => (
                      <SelectItem key={factor.id} value={factor.id.toString()} className="py-3">
                        <div className="flex flex-col gap-1 w-full">
                          <div className="flex items-center justify-between w-full">
                            <span className="font-medium text-gray-900">{factor.name}</span>
                            {factor.revision_count > 1 && (
                              <Badge variant="outline" className="ml-2 text-xs border-blue-200 text-blue-700 bg-blue-50">
                                v{factor.current_revision}
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-emerald-700">{factor.factor_value} {factor.unit}</span>
                              <span className="text-gray-400">•</span>
                              <span>{factor.source}</span>
                            </div>
                            {factor.sub_category && (
                              <div className="text-xs text-gray-500">
                                Sub-category: {factor.sub_category}
                              </div>
                            )}
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                    {!formData.category && (
                      <SelectItem value="no-category" disabled>
                        Please select a category first
                      </SelectItem>
                    )}
                    {formData.category && getEmissionFactorsByCategory(formData.category).length === 0 && (
                      <SelectItem value="no-factors" disabled>
                        No emission factors available for this category
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="amount" className="text-sm font-medium text-gray-700">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    placeholder="Enter consumption amount"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit" className="text-sm font-medium text-gray-700">Unit</Label>
                  <Input
                    id="unit"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    placeholder="e.g., kWh, L, m³, kg"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                  {formData.category && (
                    <p className="text-xs text-gray-500">
                      Suggested unit for {getCategoryInfo(formData.category).name}: {getCategoryInfo(formData.category).defaultUnit}
                    </p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes" className="text-sm font-medium text-gray-700">Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Additional information about this measurement"
                  className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500 min-h-[80px]"
                />
              </div>

              <DialogFooter className="flex gap-3 pt-6">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setIsDialogOpen(false);
                    setEditingMeasurement(null);
                    resetForm();
                  }}
                  className="border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </Button>
                <Button 
                  type="submit"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white"
                >
                  {editingMeasurement ? 'Update Measurement' : 'Add Measurement'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Enhanced Category Cards - Now Clickable */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {categories.map(category => {
          const summary = getCategorySummary(category.id);
          const IconComponent = category.icon;
          return (
            <Card 
              key={category.id} 
              className={`shadow-lg border-0 bg-gradient-to-br ${category.bgGradient} hover:shadow-xl transition-all duration-200 cursor-pointer transform hover:scale-105 ${
                activeTab === category.id ? 'ring-2 ring-emerald-500 ring-offset-2' : ''
              }`}
              onClick={() => handleCategoryTileClick(category.id)}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className={`text-sm font-semibold ${category.color.split(' ')[1]}`}>
                  {category.name}
                </CardTitle>
                <div className={`p-2 ${category.color.split(' ')[0].replace('100', '200')} rounded-lg`}>
                  <IconComponent className={`h-4 w-4 ${category.color.split(' ')[1].replace('800', '700')}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold ${category.color.split(' ')[1].replace('800', '900')}`}>
                  {summary.totalEmissions}
                </div>
                <p className={`text-sm ${category.color.split(' ')[1].replace('800', '700')} mt-1`}>
                  kgCO2e this year
                </p>
                <div className="mt-2 flex items-center justify-between">
                  <Badge className={`${category.color.split(' ')[0].replace('100', '200')} ${category.color.split(' ')[1]} hover:${category.color.split(' ')[0].replace('100', '200')}`}>
                    {summary.count} measurements
                  </Badge>
                  {activeTab === category.id && (
                    <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100">
                      Active Filter
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Enhanced Filters Section */}
      <Card className="shadow-lg border-0">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Filter className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Filters & Search</CardTitle>
                <p className="text-sm text-gray-600">Filter measurements by various criteria</p>
              </div>
            </div>
            {hasActiveFilters && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearAllFilters}
                className="text-gray-600 border-gray-300 hover:bg-gray-50"
              >
                <FilterX className="h-4 w-4 mr-2" />
                Clear All
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search emission factors, locations, or notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
            />
          </div>

          {/* Filter Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">Year</Label>
              <Select value={yearFilter} onValueChange={setYearFilter}>
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                  <SelectValue placeholder="All years" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  {getUniqueYears().map(year => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">Month</Label>
              <Select value={monthFilter} onValueChange={setMonthFilter}>
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                  <SelectValue placeholder="All months" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Months</SelectItem>
                  {months.map(month => (
                    <SelectItem key={month.value} value={month.value}>{month.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">Location</Label>
              <Select value={locationFilter} onValueChange={setLocationFilter}>
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                  <SelectValue placeholder="All locations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  {getUniqueLocations().map(location => (
                    <SelectItem key={location} value={location}>{location}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700">Active filters:</span>
              {activeTab !== 'all' && (
                <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                  Category: {getCategoryInfo(activeTab).name}
                </Badge>
              )}
              {searchTerm && (
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                  Search: "{searchTerm}"
                </Badge>
              )}
              {yearFilter !== 'all' && (
                <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                  Year: {yearFilter}
                </Badge>
              )}
              {monthFilter !== 'all' && (
                <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                  Month: {months.find(m => m.value === monthFilter)?.label}
                </Badge>
              )}
              {locationFilter !== 'all' && (
                <Badge variant="secondary" className="bg-pink-100 text-pink-800">
                  Location: {locationFilter}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Enhanced Measurements Table */}
      <Card className="shadow-lg border-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Measurements Data</CardTitle>
                <p className="text-sm text-gray-600">
                  {getFilteredMeasurements().length} measurements 
                  {hasActiveFilters && ` (filtered from ${measurements.length} total)`}
                </p>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {getFilteredMeasurements().length === 0 ? (
            <div className="text-center py-12">
              <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No measurements found</h3>
              <p className="text-gray-600 mb-4">
                {hasActiveFilters 
                  ? "No measurements match your current filters. Try adjusting your search criteria."
                  : "Get started by adding your first measurement."
                }
              </p>
              {hasActiveFilters && (
                <Button variant="outline" onClick={clearAllFilters}>
                  <FilterX className="h-4 w-4 mr-2" />
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="font-semibold">Date</TableHead>
                    <TableHead className="font-semibold">Category</TableHead>
                    <TableHead className="font-semibold">Emission Factor</TableHead>
                    <TableHead className="font-semibold">Amount</TableHead>
                    <TableHead className="font-semibold">Location</TableHead>
                    <TableHead className="font-semibold">Emissions</TableHead>
                    <TableHead className="font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {getFilteredMeasurements().map((measurement) => {
                    const categoryInfo = getCategoryInfo(measurement.emission_factor?.category);
                    const IconComponent = categoryInfo.icon;
                    return (
                      <TableRow key={measurement.id} className="hover:bg-gray-50">
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-gray-400" />
                            {new Date(measurement.date).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <IconComponent className="h-4 w-4" />
                            <Badge className={`${categoryInfo.color} border`}>
                              {categoryInfo.name}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="font-medium text-sm">{measurement.emission_factor?.name}</div>
                            <div className="text-xs text-gray-500">
                              {measurement.emission_factor?.factor_value} {measurement.emission_factor?.unit}
                              {measurement.emission_factor?.revision_count > 1 && (
                                <Badge variant="outline" className="ml-2 text-xs border-blue-200 text-blue-700">
                                  v{measurement.emission_factor?.current_revision}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">
                            {measurement.amount} {measurement.unit}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-sm text-gray-600">
                            <MapPin className="h-3 w-3" />
                            {measurement.location || 'Not specified'}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Calculator className="h-4 w-4 text-emerald-600" />
                            <span className="font-bold text-emerald-700">
                              {calculateEmissions(measurement)} kgCO2e
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(measurement)}
                              className="text-blue-600 border-blue-200 hover:bg-blue-50"
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(measurement.id)}
                              className="text-red-600 border-red-200 hover:bg-red-50"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

