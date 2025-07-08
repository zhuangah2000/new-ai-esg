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
  Search, 
  Edit, 
  Trash2, 
  Filter, 
  History, 
  ChevronDown, 
  Eye, 
  CheckCircle, 
  Clock,
  Archive,
  RotateCcw,
  Info,
  AlertCircle,
  FileText,
  Calendar,
  User,
  X,
  FilterX,
  ExternalLink,
  Link,
  Globe
} from 'lucide-react';

export function EmissionFactors({ apiBaseUrl }) {
  const [factors, setFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [scopeFilter, setScopeFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [subCategoryFilter, setSubCategoryFilter] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);
  const [editingFactor, setEditingFactor] = useState(null);
  const [selectedFactorHistory, setSelectedFactorHistory] = useState(null);
  const [revisionHistory, setRevisionHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    scope: '',
    category: '',
    sub_category: '',
    factor_value: '',
    unit: '',
    source: '',
    link: '',
    effective_date: '',
    description: '',
    revision_notes: ''
  });

  useEffect(() => {
    fetchFactors();
  }, []);

  // Reset sub-category filter when category filter changes
  useEffect(() => {
    setSubCategoryFilter('all');
  }, [categoryFilter]);

  const fetchFactors = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/emission-factors`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Fetched factors:', data);
      setFactors(data.data || data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching emission factors:', err);
      setError(err.message);
      setFactors([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchRevisionHistory = async (factorId) => {
    try {
      setLoadingHistory(true);
      const response = await fetch(`${apiBaseUrl}/emission-factors/${factorId}/revisions`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Fetched revision history:', data);
      setRevisionHistory(data.data || []);
    } catch (err) {
      console.error('Error fetching revision history:', err);
      setRevisionHistory([]);
      setError(`Failed to load revision history: ${err.message}`);
    } finally {
      setLoadingHistory(false);
    }
  };

  const validateUrl = (url) => {
    if (!url) return true; // Empty URL is valid
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const formatUrl = (url) => {
    if (!url) return '';
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return `https://${url}`;
    }
    return url;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate URL if provided
    if (formData.link && !validateUrl(formatUrl(formData.link))) {
      setError('Please enter a valid URL (e.g., https://example.com or example.com)');
      return;
    }

    try {
      const url = editingFactor 
        ? `${apiBaseUrl}/emission-factors/${editingFactor.id}/revisions`
        : `${apiBaseUrl}/emission-factors`;
      
      const method = 'POST';
      
      const payload = {
        ...formData,
		category: formData.category.toLowerCase(),
        scope: parseInt(formData.scope),
        factor_value: parseFloat(formData.factor_value),
        link: formData.link ? formatUrl(formData.link) : null
      };

      // If editing, we're creating a new revision
      if (editingFactor) {
        payload.parent_factor_id = editingFactor.id;
      }

      console.log('Submitting payload:', payload);

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to save emission factor: ${errorData}`);
      }
      
      await fetchFactors();
      setIsAddDialogOpen(false);
      setEditingFactor(null);
      resetFormData();
      setError(null);
    } catch (err) {
      console.error('Error saving emission factor:', err);
      setError(err.message);
    }
  };

  const resetFormData = () => {
    setFormData({
      name: '',
      scope: '',
      category: '',
      sub_category: '',
      factor_value: '',
      unit: '',
      source: '',
      link: '',
      effective_date: '',
      description: '',
      revision_notes: ''
    });
  };

  const handleEdit = (factor) => {
    setEditingFactor(factor);
    setFormData({
      name: factor.name,
      scope: factor.scope.toString(),
      category: factor.category,
      sub_category: factor.sub_category || '',
      factor_value: factor.factor_value.toString(),
      unit: factor.unit,
      source: factor.source,
      link: factor.link || '',
      effective_date: factor.effective_date,
      description: factor.description || '',
      revision_notes: ''
    });
    setIsAddDialogOpen(true);
  };

  const handleViewHistory = async (factor) => {
    setSelectedFactorHistory(factor);
    setIsHistoryDialogOpen(true);
    await fetchRevisionHistory(factor.id);
  };

  const handleActivateRevision = async (revisionId) => {
    try {
      const response = await fetch(`${apiBaseUrl}/emission-factors/revisions/${revisionId}/activate`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to activate revision: ${errorData}`);
      }
      
      // Refresh both the main factors list and revision history
      await fetchFactors();
      if (selectedFactorHistory) {
        await fetchRevisionHistory(selectedFactorHistory.id);
      }
      setError(null);
    } catch (err) {
      console.error('Error activating revision:', err);
      setError(err.message);
    }
  };

  const handleDeleteRevision = async (revisionId) => {
    if (!confirm('Are you sure you want to delete this revision? This action cannot be undone.')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/emission-factors/revisions/${revisionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to delete revision: ${errorData}`);
      }
      
      // Refresh both the main factors list and revision history
      await fetchFactors();
      if (selectedFactorHistory) {
        await fetchRevisionHistory(selectedFactorHistory.id);
      }
      setError(null);
    } catch (err) {
      console.error('Error deleting revision:', err);
      setError(err.message);
    }
  };

  const getScopeBadgeColor = (scope) => {
    switch (scope) {
      case 1:
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 2:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 3:
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusBadge = (isActive, isLatest) => {
    if (isActive) {
      return (
        <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
          <CheckCircle className="w-3 h-3 mr-1" />
          Active
        </Badge>
      );
    } else if (isLatest) {
      return (
        <Badge className="bg-blue-100 text-blue-800 border-blue-200">
          <Clock className="w-3 h-3 mr-1" />
          Latest
        </Badge>
      );
    } else {
      return (
        <Badge className="bg-gray-100 text-gray-800 border-gray-200">
          <Archive className="w-3 h-3 mr-1" />
          Archived
        </Badge>
      );
    }
  };

  const renderLink = (link, className = "") => {
    if (!link) return '-';
    
    const displayUrl = link.length > 30 ? `${link.substring(0, 30)}...` : link;
    
    return (
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 hover:underline ${className}`}
        title={link}
      >
        <Globe className="h-3 w-3" />
        <span className="text-sm">{displayUrl}</span>
        <ExternalLink className="h-3 w-3" />
      </a>
    );
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this emission factor? This will also delete all its revisions.')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/emission-factors/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to delete emission factor: ${errorData}`);
      }
      await fetchFactors();
      setError(null);
    } catch (err) {
      console.error('Error deleting emission factor:', err);
      setError(err.message);
    }
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    setScopeFilter('all');
    setCategoryFilter('all');
    setSubCategoryFilter('all');
  };

  // Get unique categories and subcategories for filters
  const uniqueCategories = ['all', ...new Set(factors.map(factor => factor.category).filter(Boolean))];
  
  // Get subcategories based on selected category
  const getSubCategoriesForCategory = (selectedCategory) => {
    if (selectedCategory === 'all') {
      return ['all', ...new Set(factors.map(factor => factor.sub_category).filter(Boolean))];
    } else {
      const subCategoriesForCategory = factors
        .filter(factor => factor.category === selectedCategory)
        .map(factor => factor.sub_category)
        .filter(Boolean);
      return ['all', ...new Set(subCategoriesForCategory)];
    }
  };

  const availableSubCategories = getSubCategoriesForCategory(categoryFilter);

  const filteredFactors = factors.filter((factor) => {
    const matchesSearch =
      factor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      factor.description?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesScope =
      scopeFilter === 'all' || factor.scope.toString() === scopeFilter;

    const matchesCategory =
      categoryFilter === 'all' || factor.category === categoryFilter;

    const matchesSubCategory =
      subCategoryFilter === 'all' || factor.sub_category === subCategoryFilter;

    return matchesSearch && matchesScope && matchesCategory && matchesSubCategory;
  });

  const hasActiveFilters = searchTerm || scopeFilter !== 'all' || categoryFilter !== 'all' || subCategoryFilter !== 'all';

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
          <h1 className="text-3xl font-bold text-gray-900">Emission Factors</h1>
          <p className="text-gray-600 mt-1">Manage emission factors with revision history and reference links for calculating your carbon footprint</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              onClick={() => {
                setEditingFactor(null);
                resetFormData();
              }}
              className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add New Factor
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl">
                {editingFactor ? (
                  <>
                    <Edit className="h-5 w-5 text-blue-600" />
                    Create New Revision
                  </>
                ) : (
                  <>
                    <Plus className="h-5 w-5 text-emerald-600" />
                    Add New Emission Factor
                  </>
                )}
              </DialogTitle>
              {editingFactor && (
                <Alert className="border-blue-200 bg-blue-50">
                  <Info className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    Creating a new revision for "<strong>{editingFactor.name}</strong>". The current active version will remain active until you activate this new revision from the revision history.
                  </AlertDescription>
                </Alert>
              )}
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-medium text-gray-700">Factor Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Natural Gas Combustion"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="scope" className="text-sm font-medium text-gray-700">Scope</Label>
                  <Select value={formData.scope} onValueChange={(value) => setFormData({ ...formData, scope: value })}>
                    <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                      <SelectValue placeholder="Select scope" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Scope 1 - Direct Emissions</SelectItem>
                      <SelectItem value="2">Scope 2 - Indirect Energy</SelectItem>
                      <SelectItem value="3">Scope 3 - Value Chain</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category" className="text-sm font-medium text-gray-700">Category</Label>
                  <Input
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    placeholder="e.g., fuel, electricity, transportation"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="sub_category" className="text-sm font-medium text-gray-700">Sub-category</Label>
                  <Input
                    id="sub_category"
                    value={formData.sub_category}
                    onChange={(e) => setFormData({ ...formData, sub_category: e.target.value })}
                    placeholder="e.g., natural_gas, diesel, air_travel"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="factor_value" className="text-sm font-medium text-gray-700">Factor Value</Label>
                  <Input
                    id="factor_value"
                    type="number"
                    step="any"
                    value={formData.factor_value}
                    onChange={(e) => setFormData({ ...formData, factor_value: e.target.value })}
                    placeholder="e.g., 0.233"
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
                    placeholder="e.g., kg CO2e/kWh, kg CO2e/L"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="source" className="text-sm font-medium text-gray-700">Source</Label>
                  <Input
                    id="source"
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    placeholder="e.g., EPA 2024, DEFRA 2024"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="effective_date" className="text-sm font-medium text-gray-700">Effective Date</Label>
                  <Input
                    id="effective_date"
                    type="date"
                    value={formData.effective_date}
                    onChange={(e) => setFormData({ ...formData, effective_date: e.target.value })}
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="link" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Link className="h-4 w-4" />
                  Reference Link (Optional)
                </Label>
                <Input
                  id="link"
                  type="url"
                  value={formData.link}
                  onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                  placeholder="e.g., https://www.epa.gov/ghgemissions/emission-factors or epa.gov/ghgemissions"
                  className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                />
                <p className="text-xs text-gray-500">
                  Add a link to the source documentation, methodology, or reference material
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-medium text-gray-700">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Detailed description of the emission factor, methodology, and applicable conditions"
                  className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                  rows={3}
                />
              </div>

              {editingFactor && (
                <div className="space-y-2">
                  <Label htmlFor="revision_notes" className="text-sm font-medium text-gray-700">Revision Notes *</Label>
                  <Textarea
                    id="revision_notes"
                    value={formData.revision_notes}
                    onChange={(e) => setFormData({ ...formData, revision_notes: e.target.value })}
                    placeholder="Describe what changed in this revision (e.g., Updated factor value based on latest EPA 2024 guidelines, Added reference link)"
                    className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                    rows={2}
                    required
                  />
                </div>
              )}
              
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <Button type="button" variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                  {editingFactor ? 'Create Revision' : 'Create Factor'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Enhanced Filters */}
      <Card className="shadow-sm border-gray-200">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Filter className="h-5 w-5 text-emerald-600" />
              Filters & Search
            </CardTitle>
            {hasActiveFilters && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={clearAllFilters}
                className="text-gray-500 hover:text-gray-700"
              >
                <FilterX className="h-4 w-4 mr-1" />
                Clear All
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Search Bar */}
          <div className="w-full">
            <Label htmlFor="search" className="text-sm font-medium text-gray-700 mb-2 block">Search Emission Factors</Label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                id="search"
                placeholder="Search by name or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
              />
            </div>
          </div>
          
          {/* Filter Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <Label htmlFor="scope-filter" className="text-sm font-medium text-gray-700">Scope Filter</Label>
              <Select value={scopeFilter} onValueChange={setScopeFilter}>
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                  <SelectValue placeholder="All Scopes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Scopes</SelectItem>
                  <SelectItem value="1">Scope 1 - Direct</SelectItem>
                  <SelectItem value="2">Scope 2 - Indirect Energy</SelectItem>
                  <SelectItem value="3">Scope 3 - Value Chain</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category-filter" className="text-sm font-medium text-gray-700">Category Filter</Label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  {uniqueCategories.map(category => (
                    <SelectItem key={category} value={category}>
                      {category === 'all' ? 'All Categories' : category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subcategory-filter" className="text-sm font-medium text-gray-700">
                Sub-category Filter
                {categoryFilter !== 'all' && (
                  <span className="text-xs text-gray-500 ml-1">
                    (for {categoryFilter})
                  </span>
                )}
              </Label>
              <Select 
                value={subCategoryFilter} 
                onValueChange={setSubCategoryFilter}
                disabled={categoryFilter === 'all'}
              >
                <SelectTrigger className="border-gray-300 focus:border-emerald-500 focus:ring-emerald-500 disabled:bg-gray-50 disabled:text-gray-400">
                  <SelectValue placeholder={categoryFilter === 'all' ? 'Select category first' : 'All Sub-categories'} />
                </SelectTrigger>
                <SelectContent>
                  {availableSubCategories.map(subCategory => (
                    <SelectItem key={subCategory} value={subCategory}>
                      {subCategory === 'all' ? 'All Sub-categories' : (subCategory || '(No sub-category)')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
              <span className="text-sm text-gray-600 font-medium">Active filters:</span>
              {searchTerm && (
                <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                  Search: "{searchTerm}"
                </Badge>
              )}
              {scopeFilter !== 'all' && (
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                  Scope {scopeFilter}
                </Badge>
              )}
              {categoryFilter !== 'all' && (
                <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                  Category: {categoryFilter}
                </Badge>
              )}
              {subCategoryFilter !== 'all' && (
                <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                  Sub-category: {subCategoryFilter}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card className="shadow-sm border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold text-gray-900">
              Emission Factors ({filteredFactors.length})
            </span>
            <Badge variant="outline" className="text-sm border-emerald-200 text-emerald-700">
              Showing active versions only
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-gray-200">
                  <TableHead className="font-semibold text-gray-700">Name</TableHead>
                  <TableHead className="font-semibold text-gray-700">Scope</TableHead>
                  <TableHead className="font-semibold text-gray-700">Category</TableHead>
                  <TableHead className="font-semibold text-gray-700">Sub-category</TableHead>
                  <TableHead className="font-semibold text-gray-700">Value</TableHead>
                  <TableHead className="font-semibold text-gray-700">Unit</TableHead>
                  <TableHead className="font-semibold text-gray-700">Source</TableHead>
                  <TableHead className="font-semibold text-gray-700">Link</TableHead>
                  <TableHead className="font-semibold text-gray-700">Effective Date</TableHead>
                  <TableHead className="font-semibold text-gray-700">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredFactors.map((factor) => (
                  <TableRow key={factor.id} className="border-gray-100 hover:bg-gray-50">
                    <TableCell className="font-medium">
                      <div>
                        <div className="font-semibold text-gray-900">{factor.name}</div>
                        {factor.revision_count > 1 && (
                          <Badge variant="outline" className="text-xs mt-1 border-blue-200 text-blue-700">
                            v{factor.current_revision} ({factor.revision_count} revisions)
                          </Badge>
                        )}
                        {factor.description && (
                          <div className="text-xs text-gray-500 mt-1 max-w-xs truncate" title={factor.description}>
                            {factor.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getScopeBadgeColor(factor.scope)}>
                        Scope {factor.scope}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium text-gray-700">{factor.category}</TableCell>
                    <TableCell className="text-gray-600">{factor.sub_category || '-'}</TableCell>
                    <TableCell className="font-mono font-semibold text-gray-900">{factor.factor_value}</TableCell>
                    <TableCell className="text-sm text-gray-600">{factor.unit}</TableCell>
                    <TableCell className="text-sm text-gray-600">{factor.source}</TableCell>
                    <TableCell className="max-w-xs">
                      {renderLink(factor.link)}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">{new Date(factor.effective_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(factor)}
                          className="text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                          title="Create new revision"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewHistory(factor)}
                          className="text-purple-600 hover:text-purple-800 hover:bg-purple-50"
                          title="View revision history"
                        >
                          <History className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(factor.id)}
                          className="text-red-600 hover:text-red-800 hover:bg-red-50"
                          title="Delete factor and all revisions"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {filteredFactors.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              <div className="mb-4">
                <Filter className="h-16 w-16 mx-auto text-gray-300" />
              </div>
              <p className="text-lg font-medium text-gray-700">No emission factors found</p>
              <p className="text-sm text-gray-500 mt-1">
                {factors.length === 0 
                  ? "Add your first emission factor to get started."
                  : "Try adjusting your search criteria or clearing filters."
                }
              </p>
              {hasActiveFilters && (
                <Button 
                  variant="outline" 
                  onClick={clearAllFilters}
                  className="mt-4"
                >
                  <FilterX className="h-4 w-4 mr-2" />
                  Clear All Filters
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Revision History Dialog */}
      <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
        <DialogContent className="w-[95vw] sm:max-w-[95vw] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl">
              <History className="h-5 w-5 text-purple-600" />
              Revision History: {selectedFactorHistory?.name}
            </DialogTitle>
          </DialogHeader>
          
          {loadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            </div>
          ) : revisionHistory.length > 0 ? (
            <div className="space-y-4">
              <Alert className="border-purple-200 bg-purple-50">
                <Info className="h-4 w-4 text-purple-600" />
                <AlertDescription className="text-purple-800">
                  You can activate any revision to make it the current active version. Only the active version is used for calculations. You can also delete individual revisions (except the active one).
                </AlertDescription>
              </Alert>
              
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-200">
                      <TableHead className="font-semibold text-gray-700">Version</TableHead>
                      <TableHead className="font-semibold text-gray-700">Status</TableHead>
                      <TableHead className="font-semibold text-gray-700">Factor Value</TableHead>
                      <TableHead className="font-semibold text-gray-700">Unit</TableHead>
                      <TableHead className="font-semibold text-gray-700">Source</TableHead>
                      <TableHead className="font-semibold text-gray-700">Link</TableHead>
                      <TableHead className="font-semibold text-gray-700">Effective Date</TableHead>
                      <TableHead className="font-semibold text-gray-700">Revision Notes</TableHead>
                      <TableHead className="font-semibold text-gray-700">Created</TableHead>
                      <TableHead className="font-semibold text-gray-700">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {revisionHistory.map((revision, index) => (
                      <TableRow key={revision.id} className={revision.is_active ? 'bg-emerald-50 border-emerald-200' : 'border-gray-100'}>
                        <TableCell className="font-mono font-bold text-gray-900">v{revision.version}</TableCell>
                        <TableCell>
                          {getStatusBadge(revision.is_active, index === 0)}
                        </TableCell>
                        <TableCell className="font-mono font-semibold">{revision.factor_value}</TableCell>
                        <TableCell className="text-gray-600">{revision.unit}</TableCell>
                        <TableCell className="text-gray-600">{revision.source}</TableCell>
                        <TableCell className="max-w-xs">
                          {renderLink(revision.link)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-gray-600">
                            <Calendar className="h-3 w-3 text-gray-400" />
                            {new Date(revision.effective_date).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <div className="truncate text-gray-600" title={revision.revision_notes}>
                            {revision.revision_notes || '-'}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3 text-gray-400" />
                              {new Date(revision.created_at).toLocaleDateString()}
                            </div>
                            {revision.created_by && (
                              <div className="flex items-center gap-1 text-gray-500">
                                <User className="h-3 w-3" />
                                {revision.created_by}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-1">
                            {!revision.is_active && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleActivateRevision(revision.id)}
                                className="text-emerald-600 hover:text-emerald-800 border-emerald-200 hover:bg-emerald-50"
                              >
                                <RotateCcw className="h-4 w-4 mr-1" />
                                Activate
                              </Button>
                            )}
                            {!revision.is_active && revisionHistory.length > 1 && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteRevision(revision.id)}
                                className="text-red-600 hover:text-red-800 hover:bg-red-50"
                                title="Delete this revision"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <History className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-lg font-medium">No revision history available</p>
              <p className="text-sm">This emission factor doesn't have any revisions yet.</p>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive" className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Error:</strong> {error}
            <br />
            <small>Check the browser console for more details.</small>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

