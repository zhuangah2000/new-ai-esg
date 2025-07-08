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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Plus, 
  Edit, 
  Trash2, 
  HardDrive, 
  Zap, 
  Calendar, 
  MapPin, 
  Wrench, 
  BarChart3, 
  GitCompare, 
  Filter,
  FilterX,
  Search,
  Download,
  FileSpreadsheet,
  Building2,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
  Settings,
  TrendingUp,
  DollarSign,
  Star
} from 'lucide-react';

export function Assets({ apiBaseUrl }) {
  // State management
  const [assets, setAssets] = useState([]);
  const [assetTypes, setAssetTypes] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dialog states
  const [isAddAssetDialogOpen, setIsAddAssetDialogOpen] = useState(false);
  const [isComparisonDialogOpen, setIsComparisonDialogOpen] = useState(false);
  const [isProposalDialogOpen, setIsProposalDialogOpen] = useState(false);
  
  // Form states
  const [editingAsset, setEditingAsset] = useState(null);
  const [editingComparison, setEditingComparison] = useState(null);
  const [editingProposalIndex, setEditingProposalIndex] = useState(null);
  const [selectedAssetForComparison, setSelectedAssetForComparison] = useState(null);
  
  // Filter states
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [locationFilter, setLocationFilter] = useState('all');
  const [selectedAssetFilter, setSelectedAssetFilter] = useState('all');
  
  // Asset Comparison State
  const [comparisons, setComparisons] = useState([]);
  const [filteredComparisons, setFilteredComparisons] = useState([]);
  
  // Form data states
  const [assetFormData, setAssetFormData] = useState({
    name: '',
    asset_type: '',
    model: '',
    manufacturer: '',
    serial_number: '',
    location: '',
    installation_date: '',
    capacity: '',
    capacity_unit: '',
    power_rating: '',
    efficiency_rating: '',
    annual_kwh: '',
    annual_co2e: '',
    maintenance_schedule: '',
    last_maintenance: '',
    next_maintenance: '',
    status: 'active',
    notes: ''
  });

  const [comparisonFormData, setComparisonFormData] = useState({
    name: '',
    description: '',
    current_asset_id: null,
    proposals: []
  });

  const [proposalFormData, setProposalFormData] = useState({
    name: '',
    manufacturer: '',
    model: '',
    power_rating: '',
    efficiency_rating: '',
    annual_kwh: '',
    annual_co2e: '',
    purchase_cost: '',
    installation_cost: '',
    annual_maintenance_cost: '',
    expected_lifespan: '',
    notes: ''
  });

  // Calculate summary statistics
  const summaryStats = React.useMemo(() => {
    const totalAssets = assets.length;
    const activeAssets = assets.filter(a => a.status === 'active').length;
    const totalAnnualKwh = assets.reduce((sum, asset) => sum + (parseFloat(asset.annual_kwh) || 0), 0);
    const totalAnnualCo2e = assets.reduce((sum, asset) => sum + (parseFloat(asset.annual_co2e) || 0), 0);
    
    return {
      totalAssets,
      activeAssets,
      totalAnnualKwh,
      totalAnnualCo2e: totalAnnualCo2e * 1000 // Convert tCO2e to kgCO2e
    };
  }, [assets]);

  // Filter assets based on search and filter criteria
  const filteredAssets = React.useMemo(() => {
    return assets.filter(asset => {
      const matchesSearch = (asset.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (asset.manufacturer || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (asset.model || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (asset.location || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = typeFilter === 'all' || asset.asset_type === typeFilter;
      const matchesStatus = statusFilter === 'all' || asset.status === statusFilter;
      const matchesLocation = locationFilter === 'all' || asset.location === locationFilter;
      
      return matchesSearch && matchesType && matchesStatus && matchesLocation;
    });
  }, [assets, searchTerm, typeFilter, statusFilter, locationFilter]);

  // Get unique values for filter options
  const filterOptions = React.useMemo(() => {
    const types = [...new Set(assets.map(a => a.asset_type).filter(Boolean))];
    const statuses = [...new Set(assets.map(a => a.status).filter(Boolean))];
    const locations = [...new Set(assets.map(a => a.location).filter(Boolean))];
    
    return { types, statuses, locations };
  }, [assets]);

  // Initialize data
  useEffect(() => {
    const initializeData = async () => {
      await Promise.all([
        fetchAssets(),
        fetchAssetTypes(),
        fetchSummary(),
        fetchComparisons()
      ]);
    };
    
    initializeData();
  }, [apiBaseUrl]);

  // Filter comparisons when asset filter changes
  useEffect(() => {
    if (selectedAssetFilter === 'all') {
      setFilteredComparisons(comparisons);
    } else {
      setFilteredComparisons(comparisons.filter(comp => 
        comp.current_asset_id === parseInt(selectedAssetFilter)
      ));
    }
  }, [comparisons, selectedAssetFilter]);

  // Fetch data functions
  const fetchAssets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiBaseUrl}/assets`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setAssets(data.data || []);
      } else {
        throw new Error(data.error || 'Failed to fetch assets');
      }
    } catch (error) {
      console.error('Error fetching assets:', error);
      setError(`Error fetching assets: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssetTypes = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/assets/types`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setAssetTypes(data.data || []);
      } else {
        throw new Error(data.error || 'Failed to fetch asset types');
      }
    } catch (error) {
      console.error('Error fetching asset types:', error);
      setAssetTypes([]);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/assets/summary`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setSummary(data.data || {});
      } else {
        throw new Error(data.error || 'Failed to fetch summary');
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      setSummary({});
    }
  };

  const fetchComparisons = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/asset-comparisons`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setComparisons(data.data || []);
      } else {
        throw new Error(data.error || 'Failed to fetch comparisons');
      }
    } catch (error) {
      console.error('Error fetching comparisons:', error);
      setComparisons([]);
    }
  };

  // Utility functions
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  const formatNumber = (value) => {
    if (!value) return '0';
    return parseFloat(value).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-700 bg-green-50 border-green-200';
      case 'inactive': return 'text-gray-700 bg-gray-50 border-gray-200';
      case 'maintenance': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'retired': return 'text-red-700 bg-red-50 border-red-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />;
      case 'inactive': return <XCircle className="h-4 w-4" />;
      case 'maintenance': return <Settings className="h-4 w-4" />;
      case 'retired': return <Clock className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getAssetTypeIcon = (type) => {
    switch (type) {
      case 'chiller':
      case 'aircon': return <Zap className="h-4 w-4" />;
      case 'pump':
      case 'compressor': return <Settings className="h-4 w-4" />;
      case 'boiler': return <Activity className="h-4 w-4" />;
      case 'lighting': return <Zap className="h-4 w-4" />;
      default: return <HardDrive className="h-4 w-4" />;
    }
  };

  // Handle tile clicks for filtering
  const handleTileClick = (filterType) => {
    switch (filterType) {
      case 'total':
        setStatusFilter('all');
        setTypeFilter('all');
        break;
      case 'active':
        setStatusFilter('active');
        break;
      case 'energy':
        // Sort by highest energy consumption
        setStatusFilter('all');
        break;
      case 'emissions':
        // Sort by highest emissions
        setStatusFilter('all');
        break;
    }
  };

  // Clear filters function
  const clearFilters = () => {
    setSearchTerm('');
    setTypeFilter('all');
    setStatusFilter('all');
    setLocationFilter('all');
  };

  // Asset CRUD operations
  const resetAssetForm = () => {
    setAssetFormData({
      name: '',
      asset_type: '',
      model: '',
      manufacturer: '',
      serial_number: '',
      location: '',
      installation_date: '',
      capacity: '',
      capacity_unit: '',
      power_rating: '',
      efficiency_rating: '',
      annual_kwh: '',
      annual_co2e: '',
      maintenance_schedule: '',
      last_maintenance: '',
      next_maintenance: '',
      status: 'active',
      notes: ''
    });
  };

  const handleAssetSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingAsset 
        ? `${apiBaseUrl}/assets/${editingAsset.id}`
        : `${apiBaseUrl}/assets`;
      
      const method = editingAsset ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assetFormData),
      });

      if (response.ok) {
        await fetchAssets();
        await fetchSummary();
        setIsAddAssetDialogOpen(false);
        setEditingAsset(null);
        resetAssetForm();
        setError(null);
      } else {
        throw new Error('Failed to save asset');
      }
    } catch (error) {
      console.error('Error saving asset:', error);
      setError('Failed to save asset. Please try again.');
    }
  };

  const handleEditAsset = (asset) => {
    setEditingAsset(asset);
    setAssetFormData({
      name: asset.name,
      asset_type: asset.asset_type,
      model: asset.model || '',
      manufacturer: asset.manufacturer || '',
      serial_number: asset.serial_number || '',
      location: asset.location || '',
      installation_date: asset.installation_date || '',
      capacity: asset.capacity || '',
      capacity_unit: asset.capacity_unit || '',
      power_rating: asset.power_rating || '',
      efficiency_rating: asset.efficiency_rating || '',
      annual_kwh: asset.annual_kwh || '',
      annual_co2e: asset.annual_co2e || '',
      maintenance_schedule: asset.maintenance_schedule || '',
      last_maintenance: asset.last_maintenance || '',
      next_maintenance: asset.next_maintenance || '',
      status: asset.status,
      notes: asset.notes || ''
    });
    setIsAddAssetDialogOpen(true);
  };

  const handleDeleteAsset = async (id) => {
    if (!confirm('Are you sure you want to delete this asset? This action cannot be undone.')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/assets/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchAssets();
        await fetchSummary();
        setError(null);
      } else {
        throw new Error('Failed to delete asset');
      }
    } catch (error) {
      console.error('Error deleting asset:', error);
      setError('Failed to delete asset. Please try again.');
    }
  };

  // Asset Comparison Functions
  const resetComparisonForm = () => {
    setComparisonFormData({
      name: '',
      description: '',
      current_asset_id: null,
      proposals: []
    });
    setSelectedAssetForComparison(null);
    setEditingComparison(null);
  };

  const resetProposalForm = () => {
    setProposalFormData({
      name: '',
      manufacturer: '',
      model: '',
      power_rating: '',
      efficiency_rating: '',
      annual_kwh: '',
      annual_co2e: '',
      purchase_cost: '',
      installation_cost: '',
      annual_maintenance_cost: '',
      expected_lifespan: '',
      notes: ''
    });
  };

  const handleAssetSelectionForComparison = (assetId) => {
    const asset = assets.find(a => a.id === parseInt(assetId));
    setSelectedAssetForComparison(asset);
    setComparisonFormData({
      ...comparisonFormData,
      current_asset_id: parseInt(assetId)
    });
  };

  const handleAddProposal = () => {
    setEditingProposalIndex(null);
    resetProposalForm();
    setProposalFormData({
      ...proposalFormData,
      name: `Proposal ${comparisonFormData.proposals.length + 1}`
    });
    setIsProposalDialogOpen(true);
  };

  const handleEditProposal = (index) => {
    setEditingProposalIndex(index);
    setProposalFormData(comparisonFormData.proposals[index]);
    setIsProposalDialogOpen(true);
  };

  const handleProposalSubmit = (e) => {
    e.preventDefault();
    const newProposals = [...comparisonFormData.proposals];
    
    if (editingProposalIndex !== null) {
      newProposals[editingProposalIndex] = proposalFormData;
    } else {
      newProposals.push(proposalFormData);
    }
    
    setComparisonFormData({
      ...comparisonFormData,
      proposals: newProposals
    });
    
    setIsProposalDialogOpen(false);
    resetProposalForm();
    setEditingProposalIndex(null);
  };

  const handleRemoveProposal = (index) => {
    if (!confirm('Are you sure you want to remove this proposal?')) return;
    
    const newProposals = comparisonFormData.proposals.filter((_, i) => i !== index);
    setComparisonFormData({
      ...comparisonFormData,
      proposals: newProposals
    });
  };

  const handleComparisonSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingComparison 
        ? `${apiBaseUrl}/asset-comparisons/${editingComparison.id}`
        : `${apiBaseUrl}/asset-comparisons`;
      
      const method = editingComparison ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(comparisonFormData),
      });

      if (response.ok) {
        await fetchComparisons();
        setIsComparisonDialogOpen(false);
        resetComparisonForm();
        setError(null);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save comparison');
      }
    } catch (error) {
      console.error('Error saving comparison:', error);
      setError('Failed to save comparison. Please try again.');
    }
  };

  const handleEditComparison = (comparison) => {
    setEditingComparison(comparison);
    setComparisonFormData({
      name: comparison.name,
      description: comparison.description || '',
      current_asset_id: comparison.current_asset_id,
      proposals: comparison.proposals || []
    });
    
    const asset = assets.find(a => a.id === comparison.current_asset_id);
    setSelectedAssetForComparison(asset);
    
    setIsComparisonDialogOpen(true);
  };

  const handleDeleteComparison = async (id) => {
    if (!confirm('Are you sure you want to delete this comparison?')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/asset-comparisons/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchComparisons();
        setError(null);
      } else {
        throw new Error('Failed to delete comparison');
      }
    } catch (error) {
      console.error('Error deleting comparison:', error);
      setError('Failed to delete comparison. Please try again.');
    }
  };

  const calculateSavings = (currentValue, proposalValue) => {
    if (!currentValue || !proposalValue) return '-';
    const savings = currentValue - proposalValue;
    const percentage = ((savings / currentValue) * 100).toFixed(1);
    return `${savings.toFixed(1)} (${percentage}%)`;
  };

  // Export functions
  const exportAssets = () => {
    const headers = [
      'Asset ID', 'Name', 'Type', 'Manufacturer', 'Model', 'Serial Number', 'Location',
      'Installation Date', 'Capacity', 'Capacity Unit', 'Power Rating (kW)', 'Efficiency Rating',
      'Annual kWh', 'Annual kgCO2e', 'Maintenance Schedule', 'Last Maintenance', 'Next Maintenance',
      'Status', 'Notes'
    ];
    
    const csvData = filteredAssets.map(asset => [
      asset.id,
      asset.name || '',
      asset.asset_type || '',
      asset.manufacturer || '',
      asset.model || '',
      asset.serial_number || '',
      asset.location || '',
      asset.installation_date || '',
      asset.capacity || '',
      asset.capacity_unit || '',
      asset.power_rating || '',
      asset.efficiency_rating || '',
      asset.annual_kwh || '',
      asset.annual_co2e ? (parseFloat(asset.annual_co2e) * 1000).toFixed(2) : '', // Convert to kgCO2e
      asset.maintenance_schedule || '',
      asset.last_maintenance || '',
      asset.next_maintenance || '',
      asset.status || '',
      asset.notes || ''
    ]);
    
    downloadCSV([headers, ...csvData], `assets_export_${new Date().toISOString().split('T')[0]}.csv`);
  };

  const exportComparisons = () => {
    const headers = [
      'Comparison ID', 'Name', 'Description', 'Current Asset', 'Proposal Name', 'Proposal Manufacturer',
      'Proposal Model', 'Proposal Power (kW)', 'Proposal Efficiency', 'Proposal Annual kWh',
      'Proposal Annual kgCO2e', 'Purchase Cost', 'Installation Cost', 'Annual Maintenance Cost',
      'Expected Lifespan', 'Proposal Notes'
    ];
    
    const csvData = [];
    
    filteredComparisons.forEach(comparison => {
      const currentAsset = assets.find(a => a.id === comparison.current_asset_id);
      
      if (comparison.proposals && comparison.proposals.length > 0) {
        comparison.proposals.forEach(proposal => {
          csvData.push([
            comparison.id,
            comparison.name,
            comparison.description || '',
            currentAsset ? currentAsset.name : 'Unknown',
            proposal.name || '',
            proposal.manufacturer || '',
            proposal.model || '',
            proposal.power_rating || '',
            proposal.efficiency_rating || '',
            proposal.annual_kwh || '',
            proposal.annual_co2e ? (parseFloat(proposal.annual_co2e) * 1000).toFixed(2) : '', // Convert to kgCO2e
            proposal.purchase_cost || '',
            proposal.installation_cost || '',
            proposal.annual_maintenance_cost || '',
            proposal.expected_lifespan || '',
            proposal.notes || ''
          ]);
        });
      } else {
        csvData.push([
          comparison.id,
          comparison.name,
          comparison.description || '',
          currentAsset ? currentAsset.name : 'Unknown',
          'No proposals',
          '', '', '', '', '', '', '', '', '', '', ''
        ]);
      }
    });
    
    downloadCSV([headers, ...csvData], `asset_comparisons_export_${new Date().toISOString().split('T')[0]}.csv`);
  };

  const downloadCSV = (data, filename) => {
    if (data.length === 0) return;
    
    const csvContent = data.map(row => 
      row.map(cell => `"${String(cell || '').replace(/"/g, '""')}"`).join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Asset Management</h1>
          <p className="text-gray-600 mt-1">Track and manage your physical assets for energy and emissions monitoring</p>
        </div>
        <Dialog open={isAddAssetDialogOpen} onOpenChange={setIsAddAssetDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              onClick={() => {
                setEditingAsset(null);
                resetAssetForm();
              }}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Asset
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingAsset ? 'Edit Asset' : 'Add New Asset'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAssetSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Asset Name</Label>
                  <Input
                    id="name"
                    value={assetFormData.name}
                    onChange={(e) => setAssetFormData({ ...assetFormData, name: e.target.value })}
                    placeholder="Enter asset name"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="asset_type">Asset Type</Label>
                  <Select value={assetFormData.asset_type} onValueChange={(value) => setAssetFormData({ ...assetFormData, asset_type: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select asset type" />
                    </SelectTrigger>
                    <SelectContent>
                      {assetTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="manufacturer">Manufacturer</Label>
                  <Input
                    id="manufacturer"
                    value={assetFormData.manufacturer}
                    onChange={(e) => setAssetFormData({ ...assetFormData, manufacturer: e.target.value })}
                    placeholder="Enter manufacturer"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="model">Model</Label>
                  <Input
                    id="model"
                    value={assetFormData.model}
                    onChange={(e) => setAssetFormData({ ...assetFormData, model: e.target.value })}
                    placeholder="Enter model"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="serial_number">Serial Number</Label>
                  <Input
                    id="serial_number"
                    value={assetFormData.serial_number}
                    onChange={(e) => setAssetFormData({ ...assetFormData, serial_number: e.target.value })}
                    placeholder="Enter serial number"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={assetFormData.location}
                    onChange={(e) => setAssetFormData({ ...assetFormData, location: e.target.value })}
                    placeholder="Enter location"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="installation_date">Installation Date</Label>
                  <Input
                    id="installation_date"
                    type="date"
                    value={assetFormData.installation_date}
                    onChange={(e) => setAssetFormData({ ...assetFormData, installation_date: e.target.value })}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="capacity">Capacity</Label>
                  <Input
                    id="capacity"
                    type="number"
                    step="0.01"
                    value={assetFormData.capacity}
                    onChange={(e) => setAssetFormData({ ...assetFormData, capacity: e.target.value })}
                    placeholder="Enter capacity"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="capacity_unit">Capacity Unit</Label>
                  <Select value={assetFormData.capacity_unit} onValueChange={(value) => setAssetFormData({ ...assetFormData, capacity_unit: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select unit" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="TR">TR (Tons of Refrigeration)</SelectItem>
                      <SelectItem value="HP">HP (Horsepower)</SelectItem>
                      <SelectItem value="kW">kW (Kilowatts)</SelectItem>
                      <SelectItem value="BTU/hr">BTU/hr</SelectItem>
                      <SelectItem value="CFM">CFM (Cubic Feet per Minute)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="power_rating">Power Rating (kW)</Label>
                  <Input
                    id="power_rating"
                    type="number"
                    step="0.01"
                    value={assetFormData.power_rating}
                    onChange={(e) => setAssetFormData({ ...assetFormData, power_rating: e.target.value })}
                    placeholder="Enter power rating"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="efficiency_rating">Efficiency Rating</Label>
                  <Input
                    id="efficiency_rating"
                    type="number"
                    step="0.01"
                    value={assetFormData.efficiency_rating}
                    onChange={(e) => setAssetFormData({ ...assetFormData, efficiency_rating: e.target.value })}
                    placeholder="COP, EER, etc."
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="annual_kwh">Annual kWh</Label>
                  <Input
                    id="annual_kwh"
                    type="number"
                    step="0.01"
                    value={assetFormData.annual_kwh}
                    onChange={(e) => setAssetFormData({ ...assetFormData, annual_kwh: e.target.value })}
                    placeholder="Enter annual kWh"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="annual_co2e">Annual kgCO2e</Label>
                  <Input
                    id="annual_co2e"
                    type="number"
                    step="0.01"
                    value={assetFormData.annual_co2e}
                    onChange={(e) => setAssetFormData({ ...assetFormData, annual_co2e: e.target.value })}
                    placeholder="Enter annual kgCO2e"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="maintenance_schedule">Maintenance Schedule</Label>
                  <Select value={assetFormData.maintenance_schedule} onValueChange={(value) => setAssetFormData({ ...assetFormData, maintenance_schedule: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select schedule" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Weekly">Weekly</SelectItem>
                      <SelectItem value="Monthly">Monthly</SelectItem>
                      <SelectItem value="Quarterly">Quarterly</SelectItem>
                      <SelectItem value="Semi-annually">Semi-annually</SelectItem>
                      <SelectItem value="Annually">Annually</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="last_maintenance">Last Maintenance</Label>
                  <Input
                    id="last_maintenance"
                    type="date"
                    value={assetFormData.last_maintenance}
                    onChange={(e) => setAssetFormData({ ...assetFormData, last_maintenance: e.target.value })}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="next_maintenance">Next Maintenance</Label>
                  <Input
                    id="next_maintenance"
                    type="date"
                    value={assetFormData.next_maintenance}
                    onChange={(e) => setAssetFormData({ ...assetFormData, next_maintenance: e.target.value })}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={assetFormData.status} onValueChange={(value) => setAssetFormData({ ...assetFormData, status: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="maintenance">Under Maintenance</SelectItem>
                      <SelectItem value="retired">Retired</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={assetFormData.notes}
                  onChange={(e) => setAssetFormData({ ...assetFormData, notes: e.target.value })}
                  placeholder="Additional notes about the asset"
                  rows={3}
                />
              </div>
              
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsAddAssetDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                  {editingAsset ? 'Update' : 'Create'} Asset
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

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="overview">Asset Overview</TabsTrigger>
          <TabsTrigger value="comparisons">Asset Comparisons</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card 
              className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('total')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-emerald-800">Total Assets</CardTitle>
                <HardDrive className="h-4 w-4 text-emerald-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-900">{summaryStats.totalAssets}</div>
                <p className="text-xs text-emerald-600 mt-1">All registered assets</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('active')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-800">Active Assets</CardTitle>
                <CheckCircle className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{summaryStats.activeAssets}</div>
                <p className="text-xs text-blue-600 mt-1">Currently operational</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('energy')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-amber-800">Total Annual kWh</CardTitle>
                <Zap className="h-4 w-4 text-amber-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-900">{formatNumber(summaryStats.totalAnnualKwh)}</div>
                <p className="text-xs text-amber-600 mt-1">Energy consumption</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-green-50 to-green-100 border-green-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('emissions')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-800">Total Annual kgCO2e</CardTitle>
                <BarChart3 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">{formatNumber(summaryStats.totalAnnualCo2e)}</div>
                <p className="text-xs text-green-600 mt-1">Carbon emissions</p>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-semibold text-gray-800">Search & Filter Assets</CardTitle>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={exportAssets}
                    className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export Assets
                  </Button>
                  {(searchTerm || typeFilter !== 'all' || statusFilter !== 'all' || locationFilter !== 'all') && (
                    <Button variant="outline" size="sm" onClick={clearFilters} className="text-gray-600">
                      <FilterX className="h-4 w-4 mr-2" />
                      Clear Filters
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search assets by name, manufacturer, model, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full"
                />
              </div>
              
              {/* Filter Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Asset Type</Label>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {filterOptions.types.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      {filterOptions.statuses.map(status => (
                        <SelectItem key={status} value={status}>{status}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Location</Label>
                  <Select value={locationFilter} onValueChange={setLocationFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Locations" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Locations</SelectItem>
                      {filterOptions.locations.map(location => (
                        <SelectItem key={location} value={location}>{location}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              {/* Active Filters Display */}
              {(searchTerm || typeFilter !== 'all' || statusFilter !== 'all' || locationFilter !== 'all') && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {searchTerm && (
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                      Search: "{searchTerm}"
                    </Badge>
                  )}
                  {typeFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Type: {typeFilter}
                    </Badge>
                  )}
                  {statusFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-amber-100 text-amber-800">
                      Status: {statusFilter}
                    </Badge>
                  )}
                  {locationFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Location: {locationFilter}
                    </Badge>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Assets Table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Asset Inventory ({filteredAssets.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Asset</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Power (kW)</TableHead>
                      <TableHead>Annual kWh</TableHead>
                      <TableHead>Annual kgCO2e</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredAssets.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-12 text-gray-500">
                          <HardDrive className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                          <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
                          <p className="text-gray-500">No assets match your current search criteria.</p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredAssets.map((asset) => (
                        <TableRow key={asset.id} className="hover:bg-gray-50">
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <div className="p-2 bg-gray-100 rounded-lg">
                                {getAssetTypeIcon(asset.asset_type)}
                              </div>
                              <div>
                                <div className="font-medium text-gray-900">{asset.name}</div>
                                <div className="text-sm text-gray-500">
                                  {asset.manufacturer} {asset.model}
                                </div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="capitalize">
                              {asset.asset_type}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-1">
                              <MapPin className="h-3 w-3 text-gray-400" />
                              <span className="text-sm">{asset.location || 'Not specified'}</span>
                            </div>
                          </TableCell>
                          <TableCell>{formatNumber(asset.power_rating)}</TableCell>
                          <TableCell>{formatNumber(asset.annual_kwh)}</TableCell>
                          <TableCell>
                            {asset.annual_co2e ? formatNumber(parseFloat(asset.annual_co2e) * 1000) : '0'}
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getStatusColor(asset.status)} border`}>
                              {getStatusIcon(asset.status)}
                              <span className="ml-1 capitalize">{asset.status}</span>
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleEditAsset(asset)}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
                                title="Edit Asset"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteAsset(asset.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                                title="Delete Asset"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparisons" className="space-y-6">
          {/* Comparison Header */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold">Asset Comparisons</h2>
              <p className="text-sm text-gray-600">Compare current assets with potential replacements</p>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={exportComparisons}
                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
              >
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Export Comparisons
              </Button>
              <Dialog open={isComparisonDialogOpen} onOpenChange={setIsComparisonDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    onClick={() => {
                      setEditingComparison(null);
                      resetComparisonForm();
                    }}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <GitCompare className="h-4 w-4 mr-2" />
                    New Comparison
                  </Button>
                </DialogTrigger>
                <DialogContent className="w-[90vw] sm:max-w-[90vw] max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>
                      {editingComparison ? 'Edit Asset Comparison' : 'Create Asset Comparison'}
                    </DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleComparisonSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="comparison_name">Comparison Name</Label>
                        <Input
                          id="comparison_name"
                          value={comparisonFormData.name}
                          onChange={(e) => setComparisonFormData({ ...comparisonFormData, name: e.target.value })}
                          placeholder="Enter comparison name"
                          required
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="current_asset">Current Asset</Label>
                        <Select 
                          value={comparisonFormData.current_asset_id?.toString() || ''} 
                          onValueChange={handleAssetSelectionForComparison}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select current asset" />
                          </SelectTrigger>
                          <SelectContent>
                            {assets.map(asset => (
                              <SelectItem key={asset.id} value={asset.id.toString()}>
                                {asset.name} ({asset.asset_type})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="comparison_description">Description</Label>
                      <Textarea
                        id="comparison_description"
                        value={comparisonFormData.description}
                        onChange={(e) => setComparisonFormData({ ...comparisonFormData, description: e.target.value })}
                        placeholder="Describe the purpose of this comparison"
                        rows={3}
                      />
                    </div>
                    
                    {/* Current Asset Details */}
                    {selectedAssetForComparison && (
                      <Card className="bg-blue-50 border-blue-200">
                        <CardHeader>
                          <CardTitle className="text-lg text-blue-800">Current Asset Details</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Power Rating:</span>
                              <div>{selectedAssetForComparison.power_rating || 'N/A'} kW</div>
                            </div>
                            <div>
                              <span className="font-medium">Annual kWh:</span>
                              <div>{formatNumber(selectedAssetForComparison.annual_kwh)}</div>
                            </div>
                            <div>
                              <span className="font-medium">Annual kgCO2e:</span>
                              <div>{selectedAssetForComparison.annual_co2e ? formatNumber(parseFloat(selectedAssetForComparison.annual_co2e) * 1000) : 'N/A'}</div>
                            </div>
                            <div>
                              <span className="font-medium">Efficiency:</span>
                              <div>{selectedAssetForComparison.efficiency_rating || 'N/A'}</div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                    
                    {/* Proposals Section */}
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Proposals</h3>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={handleAddProposal}
                          className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Add Proposal
                        </Button>
                      </div>
                      
                      {comparisonFormData.proposals.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <GitCompare className="h-8 w-8 mx-auto text-gray-300 mb-2" />
                          <p>No proposals added yet. Click "Add Proposal" to get started.</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {comparisonFormData.proposals.map((proposal, index) => (
                            <Card key={index} className="border border-gray-200">
                              <CardContent className="p-4">
                                <div className="flex justify-between items-start mb-3">
                                  <h4 className="font-medium">{proposal.name}</h4>
                                  <div className="flex space-x-2">
                                    <Button
                                      type="button"
                                      variant="outline"
                                      size="sm"
                                      onClick={() => handleEditProposal(index)}
                                      className="text-blue-600 hover:text-blue-700"
                                    >
                                      <Edit className="h-3 w-3" />
                                    </Button>
                                    <Button
                                      type="button"
                                      variant="outline"
                                      size="sm"
                                      onClick={() => handleRemoveProposal(index)}
                                      className="text-red-600 hover:text-red-700"
                                    >
                                      <Trash2 className="h-3 w-3" />
                                    </Button>
                                  </div>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                  <div>
                                    <span className="font-medium">Manufacturer:</span>
                                    <div>{proposal.manufacturer || 'N/A'}</div>
                                  </div>
                                  <div>
                                    <span className="font-medium">Model:</span>
                                    <div>{proposal.model || 'N/A'}</div>
                                  </div>
                                  <div>
                                    <span className="font-medium">Power Rating:</span>
                                    <div>{proposal.power_rating || 'N/A'} kW</div>
                                  </div>
                                  <div>
                                    <span className="font-medium">Annual kWh:</span>
                                    <div>{formatNumber(proposal.annual_kwh)}</div>
                                  </div>
                                </div>
                                {selectedAssetForComparison && (
                                  <div className="mt-3 pt-3 border-t border-gray-200">
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                                      <div>
                                        <span className="font-medium">Energy Savings:</span>
                                        <div className="text-green-600">
                                          {calculateSavings(
                                            parseFloat(selectedAssetForComparison.annual_kwh) || 0,
                                            parseFloat(proposal.annual_kwh) || 0
                                          )}
                                        </div>
                                      </div>
                                      <div>
                                        <span className="font-medium">CO2e Savings:</span>
                                        <div className="text-green-600">
                                          {calculateSavings(
                                            (parseFloat(selectedAssetForComparison.annual_co2e) || 0) * 1000,
                                            (parseFloat(proposal.annual_co2e) || 0) * 1000
                                          )} kgCO2e
                                        </div>
                                      </div>
                                      <div>
                                        <span className="font-medium">Purchase Cost:</span>
                                        <div>${formatNumber(proposal.purchase_cost)}</div>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsComparisonDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                        {editingComparison ? 'Update' : 'Create'} Comparison
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Comparison Filter */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Filter Comparisons</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Label>Filter by Asset</Label>
                  <Select value={selectedAssetFilter} onValueChange={setSelectedAssetFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Assets" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Assets</SelectItem>
                      {assets.map(asset => (
                        <SelectItem key={asset.id} value={asset.id.toString()}>
                          {asset.name} ({asset.asset_type})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Comparisons List */}
          <div className="space-y-4">
            {filteredComparisons.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12 text-gray-500">
                  <GitCompare className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No comparisons found</h3>
                  <p className="text-gray-500">Create your first asset comparison to get started.</p>
                </CardContent>
              </Card>
            ) : (
              filteredComparisons.map((comparison) => {
                const currentAsset = assets.find(a => a.id === comparison.current_asset_id);
                
                return (
                  <Card key={comparison.id} className="border border-gray-200 hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{comparison.name}</CardTitle>
                          <p className="text-sm text-gray-600 mt-1">{comparison.description}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            <Badge variant="outline" className="text-blue-600">
                              Current: {currentAsset ? currentAsset.name : 'Unknown Asset'}
                            </Badge>
                            <Badge variant="outline" className="text-green-600">
                              {comparison.proposals?.length || 0} Proposals
                            </Badge>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditComparison(comparison)}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteComparison(comparison.id)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    
                    {comparison.proposals && comparison.proposals.length > 0 && (
                      <CardContent>
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse">
                            <thead>
                              <tr className="border-b border-gray-200">
                                <th className="text-left p-3 font-medium text-gray-700 bg-gray-50">Specification</th>
                                <th className="text-left p-3 font-medium text-blue-700 bg-blue-50 min-w-[200px]">
                                  Current Asset
                                  <div className="text-sm font-normal text-blue-600">{currentAsset ? currentAsset.name : 'Unknown'}</div>
                                </th>
                                {comparison.proposals.map((proposal, index) => (
                                  <th key={index} className="text-left p-3 font-medium text-purple-700 bg-purple-50 min-w-[200px]">
                                    {proposal.name}
                                    <div className="text-sm font-normal text-purple-600">Proposal {index + 1}</div>
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {/* Manufacturer Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Manufacturer</td>
                                <td className="p-3 text-blue-800">{currentAsset?.manufacturer || 'N/A'}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{proposal.manufacturer || 'N/A'}</td>
                                ))}
                              </tr>
                              
                              {/* Model Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Model</td>
                                <td className="p-3 text-blue-800">{currentAsset?.model || 'N/A'}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{proposal.model || 'N/A'}</td>
                                ))}
                              </tr>
                              
                              {/* Power Rating Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Power Rating (kW)</td>
                                <td className="p-3 text-blue-800">{currentAsset?.power_rating || 'N/A'}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{proposal.power_rating || 'N/A'}</td>
                                ))}
                              </tr>
                              
                              {/* Efficiency Rating Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Efficiency Rating</td>
                                <td className="p-3 text-blue-800">{currentAsset?.efficiency_rating || 'N/A'}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{proposal.efficiency_rating || 'N/A'}</td>
                                ))}
                              </tr>
                              
                              {/* Annual kWh Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Annual kWh</td>
                                <td className="p-3 text-blue-800">{formatNumber(currentAsset?.annual_kwh)}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{formatNumber(proposal.annual_kwh)}</td>
                                ))}
                              </tr>
                              
                              {/* Annual kgCO2e Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Annual kgCO2e</td>
                                <td className="p-3 text-blue-800">
                                  {currentAsset?.annual_co2e ? formatNumber(parseFloat(currentAsset.annual_co2e) * 1000) : 'N/A'}
                                </td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">
                                    {proposal.annual_co2e ? formatNumber(parseFloat(proposal.annual_co2e) * 1000) : 'N/A'}
                                  </td>
                                ))}
                              </tr>
                              
                              {/* Purchase Cost Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Purchase Cost</td>
                                <td className="p-3 text-blue-800">Current Asset</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">${formatNumber(proposal.purchase_cost)}</td>
                                ))}
                              </tr>
                              
                              {/* Installation Cost Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Installation Cost</td>
                                <td className="p-3 text-blue-800">-</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">${formatNumber(proposal.installation_cost)}</td>
                                ))}
                              </tr>
                              
                              {/* Annual Maintenance Cost Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Annual Maintenance Cost</td>
                                <td className="p-3 text-blue-800">Current Cost</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">${formatNumber(proposal.annual_maintenance_cost)}</td>
                                ))}
                              </tr>
                              
                              {/* Expected Lifespan Row */}
                              <tr className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="p-3 font-medium text-gray-700">Expected Lifespan (years)</td>
                                <td className="p-3 text-blue-800">Current Age</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800">{proposal.expected_lifespan || 'N/A'}</td>
                                ))}
                              </tr>
                              
                              {/* Savings Section Header */}
                              <tr className="bg-green-50 border-b border-green-200">
                                <td className="p-3 font-bold text-green-800" colSpan={2 + comparison.proposals.length}>
                                  💰 Potential Savings vs Current Asset
                                </td>
                              </tr>
                              
                              {/* Energy Savings Row */}
                              <tr className="border-b border-gray-100 hover:bg-green-50">
                                <td className="p-3 font-medium text-gray-700">Energy Savings (kWh/year)</td>
                                <td className="p-3 text-blue-800">Baseline</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-green-700 font-medium">
                                    {calculateSavings(
                                      parseFloat(currentAsset?.annual_kwh) || 0,
                                      parseFloat(proposal.annual_kwh) || 0
                                    )}
                                  </td>
                                ))}
                              </tr>
                              
                              {/* CO2e Savings Row */}
                              <tr className="border-b border-gray-100 hover:bg-green-50">
                                <td className="p-3 font-medium text-gray-700">CO2e Reduction (kgCO2e/year)</td>
                                <td className="p-3 text-blue-800">Baseline</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-green-700 font-medium">
                                    {calculateSavings(
                                      (parseFloat(currentAsset?.annual_co2e) || 0) * 1000,
                                      (parseFloat(proposal.annual_co2e) || 0) * 1000
                                    )}
                                  </td>
                                ))}
                              </tr>
                              
                              {/* Notes Row */}
                              <tr className="border-b border-gray-100">
                                <td className="p-3 font-medium text-gray-700">Notes</td>
                                <td className="p-3 text-blue-800">{currentAsset?.notes || 'No notes'}</td>
                                {comparison.proposals.map((proposal, index) => (
                                  <td key={index} className="p-3 text-purple-800 text-sm">
                                    {proposal.notes || 'No notes'}
                                  </td>
                                ))}
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                );
              })
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Proposal Dialog */}
      <Dialog open={isProposalDialogOpen} onOpenChange={setIsProposalDialogOpen}>
        <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingProposalIndex !== null ? 'Edit Proposal' : 'Add New Proposal'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleProposalSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="proposal_name">Proposal Name</Label>
                <Input
                  id="proposal_name"
                  value={proposalFormData.name}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, name: e.target.value })}
                  placeholder="Enter proposal name"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_manufacturer">Manufacturer</Label>
                <Input
                  id="proposal_manufacturer"
                  value={proposalFormData.manufacturer}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, manufacturer: e.target.value })}
                  placeholder="Enter manufacturer"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_model">Model</Label>
                <Input
                  id="proposal_model"
                  value={proposalFormData.model}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, model: e.target.value })}
                  placeholder="Enter model"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_power_rating">Power Rating (kW)</Label>
                <Input
                  id="proposal_power_rating"
                  type="number"
                  step="0.01"
                  value={proposalFormData.power_rating}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, power_rating: e.target.value })}
                  placeholder="Enter power rating"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_efficiency_rating">Efficiency Rating</Label>
                <Input
                  id="proposal_efficiency_rating"
                  type="number"
                  step="0.01"
                  value={proposalFormData.efficiency_rating}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, efficiency_rating: e.target.value })}
                  placeholder="COP, EER, etc."
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_annual_kwh">Annual kWh</Label>
                <Input
                  id="proposal_annual_kwh"
                  type="number"
                  step="0.01"
                  value={proposalFormData.annual_kwh}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, annual_kwh: e.target.value })}
                  placeholder="Enter annual kWh"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_annual_co2e">Annual kgCO2e</Label>
                <Input
                  id="proposal_annual_co2e"
                  type="number"
                  step="0.01"
                  value={proposalFormData.annual_co2e}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, annual_co2e: e.target.value })}
                  placeholder="Enter annual kgCO2e"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_purchase_cost">Purchase Cost ($)</Label>
                <Input
                  id="proposal_purchase_cost"
                  type="number"
                  step="0.01"
                  value={proposalFormData.purchase_cost}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, purchase_cost: e.target.value })}
                  placeholder="Enter purchase cost"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_installation_cost">Installation Cost ($)</Label>
                <Input
                  id="proposal_installation_cost"
                  type="number"
                  step="0.01"
                  value={proposalFormData.installation_cost}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, installation_cost: e.target.value })}
                  placeholder="Enter installation cost"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_annual_maintenance_cost">Annual Maintenance Cost ($)</Label>
                <Input
                  id="proposal_annual_maintenance_cost"
                  type="number"
                  step="0.01"
                  value={proposalFormData.annual_maintenance_cost}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, annual_maintenance_cost: e.target.value })}
                  placeholder="Enter annual maintenance cost"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="proposal_expected_lifespan">Expected Lifespan (years)</Label>
                <Input
                  id="proposal_expected_lifespan"
                  type="number"
                  value={proposalFormData.expected_lifespan}
                  onChange={(e) => setProposalFormData({ ...proposalFormData, expected_lifespan: e.target.value })}
                  placeholder="Enter expected lifespan"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="proposal_notes">Notes</Label>
              <Textarea
                id="proposal_notes"
                value={proposalFormData.notes}
                onChange={(e) => setProposalFormData({ ...proposalFormData, notes: e.target.value })}
                placeholder="Additional notes about this proposal"
                rows={3}
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsProposalDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                {editingProposalIndex !== null ? 'Update' : 'Add'} Proposal
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

