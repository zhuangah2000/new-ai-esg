import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Plus, Edit, Trash2, Target, TrendingUp, Calendar, Download, Search, Filter, X } from 'lucide-react';

export function ESGTargets({ apiBaseUrl }) {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTarget, setEditingTarget] = useState(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedScope, setSelectedScope] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [activeFilters, setActiveFilters] = useState([]);

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_type: '',
    scope: '',
    baseline_value: '',
    baseline_year: '',
    target_value: '',
    target_year: '',
    unit: '',
    current_value: '',
    progress_percentage: '',
    status: 'active'
  });

  // Target types and their labels
  const targetTypes = [
    { value: 'emissions_reduction', label: 'Emissions Reduction' },
    { value: 'energy_efficiency', label: 'Energy Efficiency' },
    { value: 'renewable_energy', label: 'Renewable Energy' },
    { value: 'waste_reduction', label: 'Waste Reduction' },
    { value: 'water_conservation', label: 'Water Conservation' },
    { value: 'carbon_neutral', label: 'Carbon Neutral' },
    { value: 'net_zero', label: 'Net Zero' },
    { value: 'supplier_engagement', label: 'Supplier Engagement' },
    { value: 'other', label: 'Other' }
  ];

  const scopes = [
    { value: 1, label: 'Scope 1 - Direct Emissions' },
    { value: 2, label: 'Scope 2 - Indirect Energy' },
    { value: 3, label: 'Scope 3 - Value Chain' }
  ];

  const statuses = [
    { value: 'active', label: 'Active' },
    { value: 'achieved', label: 'Achieved' },
    { value: 'at_risk', label: 'At Risk' },
    { value: 'missed', label: 'Missed' }
  ];

  useEffect(() => {
    fetchTargets();
  }, []);

  useEffect(() => {
    updateActiveFilters();
  }, [searchTerm, selectedType, selectedScope, selectedStatus]);

  const fetchTargets = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/targets`);
      const data = await response.json();
      
      if (data.success) {
        setTargets(data.data);
      } else {
        setError(data.error || 'Failed to fetch targets');
      }
    } catch (err) {
      setError('Error fetching targets: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateActiveFilters = () => {
    const filters = [];
    if (searchTerm) filters.push({ type: 'search', value: searchTerm, label: `Search: ${searchTerm}` });
    if (selectedType !== 'all') {
      const typeLabel = targetTypes.find(t => t.value === selectedType)?.label || selectedType;
      filters.push({ type: 'type', value: selectedType, label: `Type: ${typeLabel}` });
    }
    if (selectedScope !== 'all') {
      const scopeLabel = scopes.find(s => s.value.toString() === selectedScope)?.label || `Scope ${selectedScope}`;
      filters.push({ type: 'scope', value: selectedScope, label: scopeLabel });
    }
    if (selectedStatus !== 'all') {
      const statusLabel = statuses.find(s => s.value === selectedStatus)?.label || selectedStatus;
      filters.push({ type: 'status', value: selectedStatus, label: `Status: ${statusLabel}` });
    }
    setActiveFilters(filters);
  };

  const removeFilter = (filterType) => {
    switch (filterType) {
      case 'search':
        setSearchTerm('');
        break;
      case 'type':
        setSelectedType('all');
        break;
      case 'scope':
        setSelectedScope('all');
        break;
      case 'status':
        setSelectedStatus('all');
        break;
    }
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    setSelectedType('all');
    setSelectedScope('all');
    setSelectedStatus('all');
  };

  const filteredTargets = targets.filter(target => {
    const matchesSearch = !searchTerm || 
      target.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (target.description && target.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = selectedType === 'all' || target.target_type === selectedType;
    const matchesScope = selectedScope === 'all' || target.scope?.toString() === selectedScope;
    const matchesStatus = selectedStatus === 'all' || target.status === selectedStatus;

    return matchesSearch && matchesType && matchesScope && matchesStatus;
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = editingTarget 
        ? `${apiBaseUrl}/targets/${editingTarget.id}`
        : `${apiBaseUrl}/targets`;
      
      const method = editingTarget ? 'PUT' : 'POST';
      
      // Calculate progress percentage automatically
      let calculatedProgress = 0;
      if (formData.current_value && formData.baseline_value && formData.target_value !== null && formData.target_value !== undefined) {
        const baseline = parseFloat(formData.baseline_value);
        const current = parseFloat(formData.current_value);
        const targetValue = parseFloat(formData.target_value);
        
        if (baseline < targetValue) {
          // Improvement Project
          const denominator = targetValue - baseline;
          if (denominator !== 0) {
            calculatedProgress = ((current - baseline) / denominator) * 100;
          }
        } else if (baseline > targetValue) {
          // Reduction Project
          const denominator = baseline - targetValue;
          if (denominator !== 0) {
            calculatedProgress = ((baseline - current) / denominator) * 100;
          }
        } else {
          // Baseline equals target
          calculatedProgress = current === baseline ? 100 : 0;
        }
        
        // Ensure progress is between 0 and 100
        calculatedProgress = Math.max(0, Math.min(100, calculatedProgress));
      }
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          baseline_value: parseFloat(formData.baseline_value),
          baseline_year: parseInt(formData.baseline_year),
          target_value: parseFloat(formData.target_value),
          target_year: parseInt(formData.target_year),
          scope: formData.scope && formData.scope !== 'none' ? parseInt(formData.scope) : null,
          current_value: formData.current_value ? parseFloat(formData.current_value) : null,
          progress_percentage: calculatedProgress
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        await fetchTargets();
        setIsDialogOpen(false);
        resetForm();
      } else {
        setError(data.error || 'Failed to save target');
      }
    } catch (err) {
      setError('Error saving target: ' + err.message);
    }
  };

  const handleEdit = (target) => {
    setEditingTarget(target);
    setFormData({
      name: target.name || '',
      description: target.description || '',
      target_type: target.target_type || '',
      scope: target.scope?.toString() || 'none',
      baseline_value: target.baseline_value?.toString() || '',
      baseline_year: target.baseline_year?.toString() || '',
      target_value: target.target_value?.toString() || '',
      target_year: target.target_year?.toString() || '',
      unit: target.unit || '',
      current_value: target.current_value?.toString() || '',
      status: target.status || 'active'
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (targetId) => {
    if (!window.confirm('Are you sure you want to delete this target?')) {
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/targets/${targetId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        await fetchTargets();
      } else {
        setError(data.error || 'Failed to delete target');
      }
    } catch (err) {
      setError('Error deleting target: ' + err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      target_type: '',
      scope: 'none',
      baseline_value: '',
      baseline_year: '',
      target_value: '',
      target_year: '',
      unit: '',
      current_value: '',
      status: 'active'
    });
    setEditingTarget(null);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-blue-100 text-blue-800', label: 'Active' },
      achieved: { color: 'bg-green-100 text-green-800', label: 'Achieved' },
      at_risk: { color: 'bg-yellow-100 text-yellow-800', label: 'At Risk' },
      missed: { color: 'bg-red-100 text-red-800', label: 'Missed' }
    };
    
    const config = statusConfig[status] || statusConfig.active;
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const getTypeBadge = (type) => {
    const typeConfig = {
      emissions_reduction: { color: 'bg-green-100 text-green-800', icon: '🌱' },
      energy_efficiency: { color: 'bg-blue-100 text-blue-800', icon: '⚡' },
      renewable_energy: { color: 'bg-yellow-100 text-yellow-800', icon: '☀️' },
      waste_reduction: { color: 'bg-purple-100 text-purple-800', icon: '♻️' },
      water_conservation: { color: 'bg-cyan-100 text-cyan-800', icon: '💧' },
      carbon_neutral: { color: 'bg-emerald-100 text-emerald-800', icon: '🌍' },
      net_zero: { color: 'bg-indigo-100 text-indigo-800', icon: '🎯' },
      supplier_engagement: { color: 'bg-orange-100 text-orange-800', icon: '🤝' },
      other: { color: 'bg-gray-100 text-gray-800', icon: '📋' }
    };
    
    const config = typeConfig[type] || typeConfig.other;
    const typeLabel = targetTypes.find(t => t.value === type)?.label || type;
    
    return (
      <Badge className={config.color}>
        <span className="mr-1">{config.icon}</span>
        {typeLabel}
      </Badge>
    );
  };

  const calculateProgress = (target) => {
    // If any required values are missing (null or undefined), return 0
    // Note: We check for null/undefined specifically, not falsy values, because 0 is a valid target value
    if (target.current_value === null || target.current_value === undefined || 
        target.baseline_value === null || target.baseline_value === undefined || 
        target.target_value === null || target.target_value === undefined) {
      return 0;
    }
    
    const baseline = parseFloat(target.baseline_value);
    const current = parseFloat(target.current_value);
    const targetValue = parseFloat(target.target_value);
    
    let progress = 0;
    
    if (baseline < targetValue) {
      // Improvement Project (baseline lower than target)
      // Example: Baseline 20%, Target 80%, Current 50%
      // Progress = (Current - Baseline) / (Target - Baseline)
      const denominator = targetValue - baseline;
      if (denominator !== 0) {
        progress = ((current - baseline) / denominator) * 100;
      }
    } else if (baseline > targetValue) {
      // Reduction Project (baseline higher than target)
      // Example: Baseline 1000 tCO2e, Target 700 tCO2e, Current 850 tCO2e
      // Example: Baseline 5000 kgCO2e, Target 0 kgCO2e, Current 4000 kgCO2e
      // Progress = (Baseline - Current) / (Baseline - Target)
      const denominator = baseline - targetValue;
      if (denominator !== 0) {
        progress = ((baseline - current) / denominator) * 100;
      }
    } else {
      // Baseline equals target (edge case)
      progress = current === baseline ? 100 : 0;
    }
    
    // Ensure progress is between 0 and 100
    return Math.max(0, Math.min(100, progress));
  };

  const exportTargets = () => {
    const csvData = filteredTargets.map(target => ({
      'Target Name': target.name,
      'Description': target.description || '',
      'Type': targetTypes.find(t => t.value === target.target_type)?.label || target.target_type,
      'Scope': target.scope ? `Scope ${target.scope}` : 'N/A',
      'Baseline Value': target.baseline_value,
      'Baseline Year': target.baseline_year,
      'Target Value': target.target_value,
      'Target Year': target.target_year,
      'Unit': target.unit,
      'Current Value': target.current_value || 'N/A',
      'Progress (%)': calculateProgress(target).toFixed(1),
      'Status': statuses.find(s => s.value === target.status)?.label || target.status,
      'Created': new Date(target.created_at).toLocaleDateString(),
      'Updated': new Date(target.updated_at).toLocaleDateString()
    }));

    const headers = Object.keys(csvData[0] || {});
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `esg_targets_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return new Intl.NumberFormat().format(num);
  };

  // Calculate summary statistics
  const totalTargets = targets.length;
  const activeTargets = targets.filter(t => t.status === 'active').length;
  const achievedTargets = targets.filter(t => t.status === 'achieved').length;
  const atRiskTargets = targets.filter(t => t.status === 'at_risk').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading ESG targets...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ESG Targets</h1>
          <p className="text-gray-600 mt-1">Manage and track your environmental, social, and governance targets</p>
        </div>
        <Button 
          onClick={() => {
            resetForm();
            setIsDialogOpen(true);
          }}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Target
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-l-4 border-l-emerald-500 hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-600 text-sm font-medium">Total Targets</p>
                <p className="text-3xl font-bold text-emerald-900">{totalTargets}</p>
              </div>
              <Target className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Active Targets</p>
                <p className="text-3xl font-bold text-blue-900">{activeTargets}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-l-4 border-l-green-500 hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Achieved</p>
                <p className="text-3xl font-bold text-green-900">{achievedTargets}</p>
              </div>
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-l-4 border-l-amber-500 hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-600 text-sm font-medium">At Risk</p>
                <p className="text-3xl font-bold text-amber-900">{atRiskTargets}</p>
              </div>
              <Filter className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <Card className="bg-gradient-to-r from-gray-50 to-gray-100">
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Search className="h-5 w-5 mr-2" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
            <div className="space-y-2">
              <Label>Search</Label>
              <Input
                placeholder="Search targets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Target Type</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {targetTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Scope</Label>
              <Select value={selectedScope} onValueChange={setSelectedScope}>
                <SelectTrigger>
                  <SelectValue placeholder="All Scopes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Scopes</SelectItem>
                  {scopes.map(scope => (
                    <SelectItem key={scope.value} value={scope.value.toString()}>
                      {scope.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Status</Label>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {statuses.map(status => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Actions</Label>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={clearAllFilters}
                  className="flex-1"
                >
                  Clear Filters
                </Button>
                <Button
                  variant="outline"
                  onClick={exportTargets}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Export
                </Button>
              </div>
            </div>
          </div>

          {/* Active Filters */}
          {activeFilters.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700">Active filters:</span>
              {activeFilters.map((filter, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer hover:bg-gray-300"
                  onClick={() => removeFilter(filter.type)}
                >
                  {filter.label}
                  <X className="h-3 w-3 ml-1" />
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Targets List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredTargets.map((target) => (
          <Card key={target.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg">{target.name}</CardTitle>
                  {target.description && (
                    <p className="text-gray-600 text-sm mt-1">{target.description}</p>
                  )}
                </div>
                <div className="flex space-x-2 ml-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(target)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(target.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Type and Status Badges */}
                <div className="flex flex-wrap gap-2">
                  {getTypeBadge(target.target_type)}
                  {target.scope && (
                    <Badge variant="outline">Scope {target.scope}</Badge>
                  )}
                  {getStatusBadge(target.status)}
                </div>

                {/* Target Details */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Baseline:</span>
                    <div>{formatNumber(target.baseline_value)} {target.unit} ({target.baseline_year})</div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Target:</span>
                    <div>{formatNumber(target.target_value)} {target.unit} ({target.target_year})</div>
                  </div>
                  {target.current_value && (
                    <div>
                      <span className="font-medium text-gray-700">Current:</span>
                      <div>{formatNumber(target.current_value)} {target.unit}</div>
                    </div>
                  )}
                  <div>
                    <span className="font-medium text-gray-700">Project Type:</span>
                    <div>
                      {target.baseline_value < target.target_value ? (
                        <Badge className="bg-blue-100 text-blue-800">📈 Improvement</Badge>
                      ) : target.baseline_value > target.target_value ? (
                        <Badge className="bg-green-100 text-green-800">📉 Reduction</Badge>
                      ) : (
                        <Badge className="bg-gray-100 text-gray-800">🎯 Maintain</Badge>
                      )}
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Progress</span>
                    <span>{calculateProgress(target).toFixed(1)}%</span>
                  </div>
                  <Progress value={calculateProgress(target)} className="h-2" />
                </div>

                {/* Timeline */}
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Baseline: {target.baseline_year}</span>
                  <span>Target: {target.target_year}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTargets.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No targets found</h3>
            <p className="text-gray-600 mb-4">
              {targets.length === 0 
                ? "Get started by creating your first ESG target."
                : "Try adjusting your search or filter criteria."
              }
            </p>
            <Button 
              onClick={() => {
                resetForm();
                setIsDialogOpen(true);
              }}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Target
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add/Edit Target Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-[90vw] sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingTarget ? 'Edit ESG Target' : 'Add New ESG Target'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2 space-y-2">
                <Label htmlFor="name">Target Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Enter target name"
                  required
                />
              </div>

              <div className="md:col-span-2 space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Enter target description"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_type">Target Type *</Label>
                <Select value={formData.target_type} onValueChange={(value) => setFormData({ ...formData, target_type: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select target type" />
                  </SelectTrigger>
                  <SelectContent>
                    {targetTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="scope">Scope</Label>
                <Select value={formData.scope} onValueChange={(value) => setFormData({ ...formData, scope: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select scope (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No specific scope</SelectItem>
                    {scopes.map(scope => (
                      <SelectItem key={scope.value} value={scope.value.toString()}>
                        {scope.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="baseline_value">Baseline Value *</Label>
                <Input
                  id="baseline_value"
                  type="number"
                  step="0.01"
                  value={formData.baseline_value}
                  onChange={(e) => setFormData({ ...formData, baseline_value: e.target.value })}
                  placeholder="Enter baseline value"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="baseline_year">Baseline Year *</Label>
                <Input
                  id="baseline_year"
                  type="number"
                  value={formData.baseline_year}
                  onChange={(e) => setFormData({ ...formData, baseline_year: e.target.value })}
                  placeholder="Enter baseline year"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_value">Target Value *</Label>
                <Input
                  id="target_value"
                  type="number"
                  step="0.01"
                  value={formData.target_value}
                  onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                  placeholder="Enter target value"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_year">Target Year *</Label>
                <Input
                  id="target_year"
                  type="number"
                  value={formData.target_year}
                  onChange={(e) => setFormData({ ...formData, target_year: e.target.value })}
                  placeholder="Enter target year"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="unit">Unit *</Label>
                <Input
                  id="unit"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  placeholder="e.g., kgCO2e, kWh, %"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="current_value">Current Value</Label>
                <Input
                  id="current_value"
                  type="number"
                  step="0.01"
                  value={formData.current_value}
                  onChange={(e) => setFormData({ ...formData, current_value: e.target.value })}
                  placeholder="Enter current value"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    {statuses.map(status => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                {editingTarget ? 'Update' : 'Create'} Target
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

