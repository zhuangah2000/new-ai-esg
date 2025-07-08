import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Building2, 
  Users, 
  DollarSign, 
  CheckCircle, 
  Phone, 
  Mail, 
  ExternalLink,
  Award,
  FileText,
  Calendar,
  Star,
  Save,
  X,
  Search,
  Filter,
  FilterX,
  TrendingUp,
  BarChart3,
  AlertCircle,
  MapPin,
  Calculator,
  Check,
  Minus,
  Eye,
  Shield,
  Target,
  ClipboardList,
  Download,
  FileSpreadsheet,
  FileDown
} from 'lucide-react';

export function Suppliers({ apiBaseUrl }) {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isESGDialogOpen, setIsESGDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [esgStandards, setEsgStandards] = useState([]);
  const [allESGStandards, setAllESGStandards] = useState([]); // For assessment matrix
  const [esgOptions, setEsgOptions] = useState({ standards: [], frameworks: [], assessments: [] });
  const [editingESGStandard, setEditingESGStandard] = useState(null);
  const [esgTab, setEsgTab] = useState('overview');
  const [activeTab, setActiveTab] = useState('overview');
  
  // Assessment tracking state
  const [assessmentYear, setAssessmentYear] = useState(new Date().getFullYear().toString());
  const [selectedStandard, setSelectedStandard] = useState('all');
  
  // Filtering state
  const [searchTerm, setSearchTerm] = useState('');
  const [industryFilter, setIndustryFilter] = useState('all');
  const [ratingFilter, setRatingFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    contact_person: '',
    email: '',
    phone: '',
    esg_rating: '',
    status: 'pending',
    priority_level: 'medium',
    annual_spend: '',
    notes: ''
  });

  const [esgFormData, setEsgFormData] = useState({
    standard_type: '',
    name: '',
    submission_year: new Date().getFullYear().toString(),
    document_link: '',
    status: 'active',
    score_rating: '',
    notes: ''
  });

  // Calculate summary statistics
  const summaryStats = React.useMemo(() => {
    const totalSuppliers = suppliers.length;
    const totalAnnualSpend = suppliers.reduce((sum, supplier) => {
      const spend = parseFloat(supplier.annual_spend) || 0;
      return sum + spend;
    }, 0);
    const activeSuppliers = suppliers.filter(s => s.status === 'active').length;
    const highRatingSuppliers = suppliers.filter(s => ['A', 'B'].includes(s.esg_rating)).length;
    
    return {
      totalSuppliers,
      totalAnnualSpend,
      activeSuppliers,
      highRatingSuppliers
    };
  }, [suppliers]);

  // Filter suppliers based on search and filter criteria
  const filteredSuppliers = React.useMemo(() => {
    return suppliers.filter(supplier => {
      const matchesSearch = (supplier.company_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (supplier.contact_person || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (supplier.email || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesIndustry = industryFilter === 'all' || supplier.industry === industryFilter;
      const matchesRating = ratingFilter === 'all' || supplier.esg_rating === ratingFilter;
      const matchesStatus = statusFilter === 'all' || supplier.status === statusFilter;
      
      return matchesSearch && matchesIndustry && matchesRating && matchesStatus;
    });
  }, [suppliers, searchTerm, industryFilter, ratingFilter, statusFilter]);

  // Get unique values for filter options
  const filterOptions = React.useMemo(() => {
    const industries = [...new Set(suppliers.map(s => s.industry).filter(Boolean))];
    const ratings = [...new Set(suppliers.map(s => s.esg_rating).filter(Boolean))];
    const statuses = [...new Set(suppliers.map(s => s.status).filter(Boolean))];
    
    return { industries, ratings, statuses };
  }, [suppliers]);

  // Group ESG standards by type for overview
  const groupedESGStandards = React.useMemo(() => {
    const grouped = {
      standard: esgStandards.filter(s => s.standard_type === 'standard'),
      framework: esgStandards.filter(s => s.standard_type === 'framework'),
      assessment: esgStandards.filter(s => s.standard_type === 'assessment')
    };
    return grouped;
  }, [esgStandards]);

  useEffect(() => {
    fetchSuppliers();
    fetchESGOptions();
  }, []);

  // Fetch all ESG standards when assessment tab is accessed or year/standard changes
  useEffect(() => {
    if (activeTab === 'assessments') {
      fetchAllESGStandards();
    }
  }, [activeTab, assessmentYear, selectedStandard]);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiBaseUrl}/suppliers`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const text = await response.text();
      let data;
      
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('Failed to parse JSON response:', text);
        throw new Error('Invalid JSON response from server');
      }
      
      if (data.success) {
        setSuppliers(data.data || []);
      } else {
        setError(data.error || 'Failed to fetch suppliers');
      }
    } catch (err) {
      console.error('Error fetching suppliers:', err);
      setError('Error fetching suppliers: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchESGOptions = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/esg-standards/options`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const text = await response.text();
      let data;
      
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('Failed to parse ESG options JSON:', text);
        return;
      }
      
      if (data.success) {
        setEsgOptions(data.data || { standards: [], frameworks: [], assessments: [] });
      }
    } catch (err) {
      console.error('Error fetching ESG options:', err);
    }
  };

  const fetchSupplierESGStandards = async (supplierId) => {
    try {
      const response = await fetch(`${apiBaseUrl}/suppliers/${supplierId}/esg-standards`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setEsgStandards(data.data || []);
      }
    } catch (err) {
      console.error('Error fetching ESG standards:', err);
      setEsgStandards([]);
    }
  };

  // Fetch all ESG standards for all suppliers for assessment matrix
  const fetchAllESGStandards = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/suppliers/assessments?year=${assessmentYear}&standard=${selectedStandard}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        // Flatten the assessment data to create a lookup map
        const allStandards = [];
        data.data.forEach(supplierData => {
          supplierData.assessments.forEach(assessment => {
            allStandards.push({
              ...assessment,
              supplier_id: supplierData.supplier_id
            });
          });
        });
        setAllESGStandards(allStandards);
      }
    } catch (err) {
      console.error('Error fetching all ESG standards:', err);
      setAllESGStandards([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = editingSupplier 
        ? `${apiBaseUrl}/suppliers/${editingSupplier.id}`
        : `${apiBaseUrl}/suppliers`;
      
      const method = editingSupplier ? 'PUT' : 'POST';
      
      // Ensure annual_spend is a number
      const submitData = {
        ...formData,
        annual_spend: formData.annual_spend === '' ? 0 : parseFloat(formData.annual_spend) || 0
      };
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        await fetchSuppliers();
        setIsDialogOpen(false);
        resetForm();
        setError(null);
        // Refresh assessment matrix if on that tab
        if (activeTab === 'assessments') {
          fetchAllESGStandards();
        }
      } else {
        setError(data.error || 'Failed to save supplier');
      }
    } catch (err) {
      console.error('Error saving supplier:', err);
      setError('Error saving supplier: ' + err.message);
    }
  };

  const handleESGSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = editingESGStandard 
        ? `${apiBaseUrl}/suppliers/${selectedSupplier.id}/esg-standards/${editingESGStandard.id}`
        : `${apiBaseUrl}/suppliers/${selectedSupplier.id}/esg-standards`;
      
      const method = editingESGStandard ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(esgFormData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        await fetchSupplierESGStandards(selectedSupplier.id);
        resetESGForm();
        setError(null);
        // Switch back to overview tab after adding
        if (!editingESGStandard) {
          setEsgTab('overview');
        }
        // Refresh assessment matrix data
        fetchAllESGStandards();
      } else {
        setError(data.error || 'Failed to save ESG standard');
      }
    } catch (err) {
      console.error('Error saving ESG standard:', err);
      setError('Error saving ESG standard: ' + err.message);
    }
  };

  const handleDelete = async (supplierId) => {
    if (!window.confirm('Are you sure you want to delete this supplier?')) {
      return;
    }
    
    try {
      const response = await fetch(`${apiBaseUrl}/suppliers/${supplierId}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        await fetchSuppliers();
        setError(null);
        // Refresh assessment matrix if on that tab
        if (activeTab === 'assessments') {
          fetchAllESGStandards();
        }
      } else {
        setError(data.error || 'Failed to delete supplier');
      }
    } catch (err) {
      console.error('Error deleting supplier:', err);
      setError('Error deleting supplier: ' + err.message);
    }
  };

  const handleDeleteESGStandard = async (standardId) => {
    if (!window.confirm('Are you sure you want to delete this ESG standard?')) {
      return;
    }
    
    try {
      const response = await fetch(`${apiBaseUrl}/suppliers/${selectedSupplier.id}/esg-standards/${standardId}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        await fetchSupplierESGStandards(selectedSupplier.id);
        setError(null);
        // Refresh assessment matrix data
        fetchAllESGStandards();
      } else {
        setError(data.error || 'Failed to delete ESG standard');
      }
    } catch (err) {
      console.error('Error deleting ESG standard:', err);
      setError('Error deleting ESG standard: ' + err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      company_name: '',
      industry: '',
      contact_person: '',
      email: '',
      phone: '',
      esg_rating: '',
      status: 'pending',
      priority_level: 'medium',
      annual_spend: '',
      notes: ''
    });
    setEditingSupplier(null);
  };

  const resetESGForm = () => {
    setEsgFormData({
      standard_type: '',
      name: '',
      submission_year: new Date().getFullYear().toString(),
      document_link: '',
      status: 'active',
      score_rating: '',
      notes: ''
    });
    setEditingESGStandard(null);
  };

  const openEditDialog = (supplier) => {
    setEditingSupplier(supplier);
    setFormData({
      company_name: supplier.company_name || '',
      industry: supplier.industry || '',
      contact_person: supplier.contact_person || '',
      email: supplier.email || '',
      phone: supplier.phone || '',
      esg_rating: supplier.esg_rating || '',
      status: supplier.status || 'pending',
      priority_level: supplier.priority_level || 'medium',
      annual_spend: supplier.annual_spend?.toString() || '',
      notes: supplier.notes || ''
    });
    setIsDialogOpen(true);
  };

  const openESGDialog = (supplier) => {
    setSelectedSupplier(supplier);
    setIsESGDialogOpen(true);
    setEsgTab('overview');
    fetchSupplierESGStandards(supplier.id);
  };

  const openEditESGDialog = (standard) => {
    setEditingESGStandard(standard);
    setEsgFormData({
      standard_type: standard.standard_type || '',
      name: standard.name || '',
      submission_year: standard.submission_year?.toString() || new Date().getFullYear().toString(),
      document_link: standard.document_link || '',
      status: standard.status || 'active',
      score_rating: standard.score_rating || '',
      notes: standard.notes || ''
    });
    setEsgTab('overview');
  };

  const clearFilters = () => {
    setSearchTerm('');
    setIndustryFilter('all');
    setRatingFilter('all');
    setStatusFilter('all');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'active': return 'default';
      case 'pending': return 'secondary';
      case 'inactive': return 'outline';
      default: return 'secondary';
    }
  };

  const getRatingBadgeVariant = (rating) => {
    switch (rating) {
      case 'A': return 'default';
      case 'B': return 'secondary';
      case 'C': return 'outline';
      case 'D': return 'destructive';
      case 'F': return 'destructive';
      default: return 'outline';
    }
  };

  const getPriorityBadgeVariant = (priority) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'secondary';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-700 bg-green-50 border-green-200';
      case 'pending': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'inactive': return 'text-gray-700 bg-gray-50 border-gray-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'A': return 'text-green-700 bg-green-50 border-green-200';
      case 'B': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'C': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'D': return 'text-orange-700 bg-orange-50 border-orange-200';
      case 'F': return 'text-red-700 bg-red-50 border-red-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-700 bg-red-50 border-red-200';
      case 'medium': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'low': return 'text-gray-700 bg-gray-50 border-gray-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  // Check if supplier has submitted assessment for a standard based on allESGStandards
  const hasSubmittedAssessment = (supplierId, standardName) => {
    return allESGStandards.some(esg => 
      esg.supplier_id === supplierId && 
      esg.standard_name === standardName && 
      esg.submission_year?.toString() === assessmentYear &&
      esg.status === 'active'
    );
  };

  // Get all available standards for assessment matrix from ESG options
  const allStandards = React.useMemo(() => {
    const standards = new Set();
    
    // Add standards from ESG options
    esgOptions.standards?.forEach(std => standards.add(std));
    esgOptions.frameworks?.forEach(std => standards.add(std));
    esgOptions.assessments?.forEach(std => standards.add(std));
    
    return Array.from(standards).sort();
  }, [esgOptions]);

  // Export functions
  const exportSuppliersToCSV = () => {
    const headers = [
      'ID', 'Company Name', 'Industry', 'Contact Person', 'Email', 'Phone',
      'ESG Rating', 'Status', 'Priority Level', 'Annual Spend', 'Notes'
    ];
    
    const csvData = filteredSuppliers.map(supplier => [
      supplier.id,
      supplier.company_name || '',
      supplier.industry || '',
      supplier.contact_person || '',
      supplier.email || '',
      supplier.phone || '',
      supplier.esg_rating || '',
      supplier.status || '',
      supplier.priority_level || '',
      supplier.annual_spend || 0,
      (supplier.notes || '').replace(/"/g, '""') // Escape quotes
    ]);
    
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.map(field => `"${field}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `suppliers_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportAssessmentMatrixToCSV = () => {
    const standardsToShow = selectedStandard === 'all' ? allStandards : [selectedStandard];
    
    const headers = ['Supplier ID', 'Company Name', ...standardsToShow];
    
    const csvData = suppliers.map(supplier => {
      const row = [supplier.id, supplier.company_name];
      standardsToShow.forEach(standard => {
        const hasSubmitted = hasSubmittedAssessment(supplier.id, standard);
        row.push(hasSubmitted ? 'Yes' : 'No');
      });
      return row;
    });
    
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.map(field => `"${field}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `assessment_matrix_${assessmentYear}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Supplier Management</h1>
          <p className="text-gray-600 mt-1">Manage your supply chain ESG compliance and assessments</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm} className="bg-emerald-600 hover:bg-emerald-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Supplier
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="company_name">Company Name *</Label>
                  <Input
                    id="company_name"
                    value={formData.company_name}
                    onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                    required
                    placeholder="Enter company name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="industry">Industry</Label>
                  <Input
                    id="industry"
                    value={formData.industry}
                    onChange={(e) => setFormData({...formData, industry: e.target.value})}
                    placeholder="e.g., Manufacturing, Technology"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="contact_person">Contact Person</Label>
                  <Input
                    id="contact_person"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({...formData, contact_person: e.target.value})}
                    placeholder="Primary contact name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="contact@company.com"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="annual_spend">Annual Spend ($)</Label>
                  <Input
                    id="annual_spend"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.annual_spend}
                    onChange={(e) => setFormData({...formData, annual_spend: e.target.value})}
                    placeholder="0.00"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="esg_rating">ESG Rating</Label>
                  <Select value={formData.esg_rating} onValueChange={(value) => setFormData({...formData, esg_rating: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select rating" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A">A - Excellent</SelectItem>
                      <SelectItem value="B">B - Good</SelectItem>
                      <SelectItem value="C">C - Average</SelectItem>
                      <SelectItem value="D">D - Below Average</SelectItem>
                      <SelectItem value="F">F - Poor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status} onValueChange={(value) => setFormData({...formData, status: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="priority_level">Priority Level</Label>
                  <Select value={formData.priority_level} onValueChange={(value) => setFormData({...formData, priority_level: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Additional notes about this supplier..."
                  rows={3}
                />
              </div>
              
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                  {editingSupplier ? 'Update' : 'Create'} Supplier
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
          <TabsTrigger value="overview">Supplier Overview</TabsTrigger>
          <TabsTrigger value="assessments">Assessment Tracking</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-emerald-800">Total Suppliers</CardTitle>
                <Building2 className="h-4 w-4 text-emerald-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-900">{summaryStats.totalSuppliers}</div>
                <p className="text-xs text-emerald-600 mt-1">Active partnerships</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-800">High Rating (A-B)</CardTitle>
                <Star className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{summaryStats.highRatingSuppliers}</div>
                <p className="text-xs text-blue-600 mt-1">Excellent ESG performers</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-amber-800">Total Annual Spend</CardTitle>
                <DollarSign className="h-4 w-4 text-amber-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-900">{formatCurrency(summaryStats.totalAnnualSpend)}</div>
                <p className="text-xs text-amber-600 mt-1">Total procurement value</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-800">Active Suppliers</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">{summaryStats.activeSuppliers}</div>
                <p className="text-xs text-green-600 mt-1">Currently engaged</p>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-semibold text-gray-800">Search & Filter Suppliers</CardTitle>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={exportSuppliersToCSV}
                    className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export Suppliers
                  </Button>
                  {(searchTerm || industryFilter !== 'all' || ratingFilter !== 'all' || statusFilter !== 'all') && (
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
                  placeholder="Search suppliers by name, contact, or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full"
                />
              </div>
              
              {/* Filter Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Industry</Label>
                  <Select value={industryFilter} onValueChange={setIndustryFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Industries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Industries</SelectItem>
                      {filterOptions.industries.map(industry => (
                        <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>ESG Rating</Label>
                  <Select value={ratingFilter} onValueChange={setRatingFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Ratings" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Ratings</SelectItem>
                      {filterOptions.ratings.map(rating => (
                        <SelectItem key={rating} value={rating}>{rating}</SelectItem>
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
              </div>
              
              {/* Active Filters Display */}
              {(searchTerm || industryFilter !== 'all' || ratingFilter !== 'all' || statusFilter !== 'all') && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {searchTerm && (
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                      Search: "{searchTerm}"
                    </Badge>
                  )}
                  {industryFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Industry: {industryFilter}
                    </Badge>
                  )}
                  {ratingFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-amber-100 text-amber-800">
                      Rating: {ratingFilter}
                    </Badge>
                  )}
                  {statusFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Status: {statusFilter}
                    </Badge>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Beautified Suppliers Table */}
          <Card>
            <CardHeader>
              <CardTitle>Suppliers ({filteredSuppliers.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead className="w-16 font-semibold">ID</TableHead>
                      <TableHead className="font-semibold">Company Details</TableHead>
                      <TableHead className="font-semibold">Contact Information</TableHead>
                      <TableHead className="font-semibold text-center">ESG Rating</TableHead>
                      <TableHead className="font-semibold text-right">Annual Spend</TableHead>
                      <TableHead className="font-semibold text-center">Status</TableHead>
                      <TableHead className="font-semibold text-center">Priority</TableHead>
                      <TableHead className="font-semibold text-center">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredSuppliers.map((supplier, index) => (
                      <TableRow 
                        key={supplier.id} 
                        className={`hover:bg-gray-50 transition-colors ${
                          index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                        }`}
                      >
                        <TableCell className="font-mono text-sm text-gray-500 bg-gray-50">
                          #{supplier.id}
                        </TableCell>
                        
                        <TableCell className="max-w-xs">
                          <div className="space-y-1">
                            <div className="font-semibold text-gray-900 truncate">
                              {supplier.company_name}
                            </div>
                            <div className="text-sm text-gray-600 flex items-center">
                              <Building2 className="h-3 w-3 mr-1 text-gray-400" />
                              {supplier.industry || 'Not specified'}
                            </div>
                          </div>
                        </TableCell>
                        
                        <TableCell className="max-w-xs">
                          <div className="space-y-1">
                            {supplier.contact_person && (
                              <div className="font-medium text-gray-900 truncate">
                                {supplier.contact_person}
                              </div>
                            )}
                            {supplier.email && (
                              <div className="flex items-center text-sm text-gray-600 truncate">
                                <Mail className="h-3 w-3 mr-1 text-gray-400 flex-shrink-0" />
                                <span className="truncate">{supplier.email}</span>
                              </div>
                            )}
                            {supplier.phone && (
                              <div className="flex items-center text-sm text-gray-600">
                                <Phone className="h-3 w-3 mr-1 text-gray-400 flex-shrink-0" />
                                {supplier.phone}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-center">
                          {supplier.esg_rating ? (
                            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRatingColor(supplier.esg_rating)}`}>
                              <Star className="h-3 w-3 mr-1" />
                              {supplier.esg_rating}
                            </div>
                          ) : (
                            <span className="text-gray-400 text-sm">Not rated</span>
                          )}
                        </TableCell>
                        
                        <TableCell className="text-right">
                          <div className="font-semibold text-gray-900">
                            {formatCurrency(supplier.annual_spend)}
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-center">
                          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(supplier.status)}`}>
                            <div className={`w-2 h-2 rounded-full mr-2 ${
                              supplier.status === 'active' ? 'bg-green-500' :
                              supplier.status === 'pending' ? 'bg-yellow-500' : 'bg-gray-500'
                            }`}></div>
                            {supplier.status}
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-center">
                          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getPriorityColor(supplier.priority_level)}`}>
                            {supplier.priority_level}
                          </div>
                        </TableCell>
                        
                        <TableCell>
                          <div className="flex justify-center space-x-1">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openESGDialog(supplier)}
                              className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 border-emerald-200"
                              title="Manage ESG Standards"
                            >
                              <Award className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openEditDialog(supplier)}
                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
                              title="Edit Supplier"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(supplier.id)}
                              className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                              title="Delete Supplier"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {filteredSuppliers.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <Building2 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No suppliers found</h3>
                    <p className="text-gray-500">No suppliers match your current search criteria.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assessments" className="space-y-6">
          {/* Assessment Filters */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Assessment Tracking Matrix</CardTitle>
                  <p className="text-sm text-gray-600">Track which suppliers have submitted ESG assessments by year and standard</p>
                </div>
                <Button 
                  variant="outline" 
                  onClick={exportAssessmentMatrixToCSV}
                  className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                >
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  Export Matrix
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Year</Label>
                  <Select value={assessmentYear} onValueChange={setAssessmentYear}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2025">2025</SelectItem>
                      <SelectItem value="2024">2024</SelectItem>
                      <SelectItem value="2023">2023</SelectItem>
                      <SelectItem value="2022">2022</SelectItem>
                      <SelectItem value="2021">2021</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Standard/Framework</Label>
                  <Select value={selectedStandard} onValueChange={setSelectedStandard}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Standards</SelectItem>
                      {allStandards.map(standard => (
                        <SelectItem key={standard} value={standard}>{standard}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Assessment Matrix */}
          <Card>
            <CardHeader>
              <CardTitle>Assessment Submission Matrix - {assessmentYear}</CardTitle>
              <p className="text-sm text-gray-600">
                {selectedStandard === 'all' ? 'All Standards' : selectedStandard}
              </p>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead className="min-w-[200px] font-semibold">Supplier</TableHead>
                      {(selectedStandard === 'all' ? allStandards : [selectedStandard]).map(standard => (
                        <TableHead key={standard} className="text-center min-w-[120px] font-semibold">
                          {standard}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {suppliers.map((supplier, index) => (
                      <TableRow 
                        key={supplier.id}
                        className={`hover:bg-gray-50 transition-colors ${
                          index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                        }`}
                      >
                        <TableCell className="font-medium">
                          <div className="space-y-1">
                            <div className="font-semibold text-gray-900">{supplier.company_name}</div>
                            <div className="text-sm text-gray-500">ID: {supplier.id}</div>
                          </div>
                        </TableCell>
                        {(selectedStandard === 'all' ? allStandards : [selectedStandard]).map(standard => (
                          <TableCell key={standard} className="text-center">
                            {hasSubmittedAssessment(supplier.id, standard) ? (
                              <div className="inline-flex items-center justify-center w-8 h-8 bg-green-100 rounded-full">
                                <Check className="h-5 w-5 text-green-600" />
                              </div>
                            ) : (
                              <div className="inline-flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full">
                                <Minus className="h-4 w-4 text-gray-400" />
                              </div>
                            )}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {suppliers.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No suppliers available for assessment tracking.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Enhanced ESG Standards Dialog */}
      <Dialog open={isESGDialogOpen} onOpenChange={setIsESGDialogOpen}>
        <DialogContent className="w-[95vw] sm:max-w-[95vw] max-h-[95vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Award className="h-5 w-5 text-emerald-600" />
              <span>ESG Supplier Management - {selectedSupplier?.company_name}</span>
            </DialogTitle>
          </DialogHeader>
          
          <Tabs value={esgTab} onValueChange={setEsgTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview" className="flex items-center space-x-2">
                <Eye className="h-4 w-4" />
                <span>Overview</span>
              </TabsTrigger>
              <TabsTrigger value="add-standard" className="flex items-center space-x-2">
                <Shield className="h-4 w-4" />
                <span>Add Standard</span>
              </TabsTrigger>
              <TabsTrigger value="add-framework" className="flex items-center space-x-2">
                <Target className="h-4 w-4" />
                <span>Add Framework</span>
              </TabsTrigger>
              <TabsTrigger value="add-assessment" className="flex items-center space-x-2">
                <ClipboardList className="h-4 w-4" />
                <span>Add Assessment</span>
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab - Shows all existing records */}
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Standards */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-lg">
                      <Shield className="h-5 w-5 text-blue-600" />
                      <span>Standards ({groupedESGStandards.standard.length})</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {groupedESGStandards.standard.map(standard => (
                      <div key={standard.id} className="p-3 border rounded-lg bg-blue-50 border-blue-200">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-blue-900 truncate">{standard.name}</div>
                            <div className="text-sm text-blue-700 mt-1">
                              Year: {standard.submission_year || 'N/A'}
                              {standard.score_rating && (
                                <span className="ml-2 px-2 py-1 bg-blue-200 text-blue-800 rounded text-xs">
                                  {standard.score_rating}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center mt-2">
                              <div className={`w-2 h-2 rounded-full mr-2 ${
                                standard.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                              }`}></div>
                              <span className="text-xs text-blue-600">{standard.status}</span>
                            </div>
                          </div>
                          <div className="flex space-x-1 ml-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openEditESGDialog(standard)}
                              className="text-blue-600 hover:text-blue-700"
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteESGStandard(standard.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        {standard.document_link && (
                          <a 
                            href={standard.document_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-xs text-blue-600 hover:text-blue-700 mt-2"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View Document
                          </a>
                        )}
                      </div>
                    ))}
                    {groupedESGStandards.standard.length === 0 && (
                      <div className="text-center py-4 text-gray-500">
                        <Shield className="h-8 w-8 mx-auto text-gray-300 mb-2" />
                        <p className="text-sm">No standards added yet</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Frameworks */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-lg">
                      <Target className="h-5 w-5 text-green-600" />
                      <span>Frameworks ({groupedESGStandards.framework.length})</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {groupedESGStandards.framework.map(framework => (
                      <div key={framework.id} className="p-3 border rounded-lg bg-green-50 border-green-200">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-green-900 truncate">{framework.name}</div>
                            <div className="text-sm text-green-700 mt-1">
                              Year: {framework.submission_year || 'N/A'}
                              {framework.score_rating && (
                                <span className="ml-2 px-2 py-1 bg-green-200 text-green-800 rounded text-xs">
                                  {framework.score_rating}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center mt-2">
                              <div className={`w-2 h-2 rounded-full mr-2 ${
                                framework.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                              }`}></div>
                              <span className="text-xs text-green-600">{framework.status}</span>
                            </div>
                          </div>
                          <div className="flex space-x-1 ml-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openEditESGDialog(framework)}
                              className="text-green-600 hover:text-green-700"
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteESGStandard(framework.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        {framework.document_link && (
                          <a 
                            href={framework.document_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-xs text-green-600 hover:text-green-700 mt-2"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View Document
                          </a>
                        )}
                      </div>
                    ))}
                    {groupedESGStandards.framework.length === 0 && (
                      <div className="text-center py-4 text-gray-500">
                        <Target className="h-8 w-8 mx-auto text-gray-300 mb-2" />
                        <p className="text-sm">No frameworks added yet</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Assessments */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-lg">
                      <ClipboardList className="h-5 w-5 text-purple-600" />
                      <span>Assessments ({groupedESGStandards.assessment.length})</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {groupedESGStandards.assessment.map(assessment => (
                      <div key={assessment.id} className="p-3 border rounded-lg bg-purple-50 border-purple-200">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-purple-900 truncate">{assessment.name}</div>
                            <div className="text-sm text-purple-700 mt-1">
                              Year: {assessment.submission_year || 'N/A'}
                              {assessment.score_rating && (
                                <span className="ml-2 px-2 py-1 bg-purple-200 text-purple-800 rounded text-xs">
                                  {assessment.score_rating}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center mt-2">
                              <div className={`w-2 h-2 rounded-full mr-2 ${
                                assessment.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                              }`}></div>
                              <span className="text-xs text-purple-600">{assessment.status}</span>
                            </div>
                          </div>
                          <div className="flex space-x-1 ml-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openEditESGDialog(assessment)}
                              className="text-purple-600 hover:text-purple-700"
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteESGStandard(assessment.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        {assessment.document_link && (
                          <a 
                            href={assessment.document_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-xs text-purple-600 hover:text-purple-700 mt-2"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View Document
                          </a>
                        )}
                      </div>
                    ))}
                    {groupedESGStandards.assessment.length === 0 && (
                      <div className="text-center py-4 text-gray-500">
                        <ClipboardList className="h-8 w-8 mx-auto text-gray-300 mb-2" />
                        <p className="text-sm">No assessments added yet</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Edit Form for selected ESG item */}
              {editingESGStandard && (
                <Card className="border-2 border-emerald-200 bg-emerald-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Edit className="h-5 w-5 text-emerald-600" />
                      <span>Edit {editingESGStandard.standard_type}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleESGSubmit} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Name *</Label>
                          <Select 
                            value={esgFormData.name} 
                            onValueChange={(value) => setEsgFormData({...esgFormData, name: value})}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder={`Select ${editingESGStandard.standard_type}`} />
                            </SelectTrigger>
                            <SelectContent>
                              {esgOptions[editingESGStandard.standard_type + 's']?.map(option => (
                                <SelectItem key={option} value={option}>{option}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div className="space-y-2">
                          <Label>Submission Year</Label>
                          <Input
                            type="number"
                            min="2020"
                            max="2030"
                            value={esgFormData.submission_year}
                            onChange={(e) => setEsgFormData({...esgFormData, submission_year: e.target.value})}
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label>Score/Rating</Label>
                          <Input
                            value={esgFormData.score_rating}
                            onChange={(e) => setEsgFormData({...esgFormData, score_rating: e.target.value})}
                            placeholder="e.g., A+, 85%, 4.5/5"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label>Status</Label>
                          <Select 
                            value={esgFormData.status} 
                            onValueChange={(value) => setEsgFormData({...esgFormData, status: value})}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="active">Active</SelectItem>
                              <SelectItem value="expired">Expired</SelectItem>
                              <SelectItem value="pending">Pending</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div className="space-y-2 md:col-span-2">
                          <Label>Document Link</Label>
                          <Input
                            type="url"
                            value={esgFormData.document_link}
                            onChange={(e) => setEsgFormData({...esgFormData, document_link: e.target.value})}
                            placeholder="https://..."
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Notes</Label>
                        <Textarea
                          value={esgFormData.notes}
                          onChange={(e) => setEsgFormData({...esgFormData, notes: e.target.value})}
                          placeholder="Additional notes..."
                          rows={2}
                        />
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                          <Save className="h-4 w-4 mr-2" />
                          Update {editingESGStandard.standard_type}
                        </Button>
                        <Button type="button" variant="outline" onClick={resetESGForm}>
                          <X className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Add Standard Tab */}
            <TabsContent value="add-standard" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <span>Add New Standard</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleESGSubmit} className="space-y-4">
                    <input type="hidden" value="standard" onChange={(e) => setEsgFormData({...esgFormData, standard_type: 'standard'})} />
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Standard Name *</Label>
                        <Select 
                          value={esgFormData.name} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, name: value, standard_type: 'standard'})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select standard" />
                          </SelectTrigger>
                          <SelectContent>
                            {esgOptions.standards?.map(option => (
                              <SelectItem key={option} value={option}>{option}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Submission Year</Label>
                        <Input
                          type="number"
                          min="2020"
                          max="2030"
                          value={esgFormData.submission_year}
                          onChange={(e) => setEsgFormData({...esgFormData, submission_year: e.target.value})}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Score/Rating</Label>
                        <Input
                          value={esgFormData.score_rating}
                          onChange={(e) => setEsgFormData({...esgFormData, score_rating: e.target.value})}
                          placeholder="e.g., A+, 85%, 4.5/5"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Status</Label>
                        <Select 
                          value={esgFormData.status} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, status: value})}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="active">Active</SelectItem>
                            <SelectItem value="expired">Expired</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label>Document Link</Label>
                        <Input
                          type="url"
                          value={esgFormData.document_link}
                          onChange={(e) => setEsgFormData({...esgFormData, document_link: e.target.value})}
                          placeholder="https://..."
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Notes</Label>
                      <Textarea
                        value={esgFormData.notes}
                        onChange={(e) => setEsgFormData({...esgFormData, notes: e.target.value})}
                        placeholder="Additional notes..."
                        rows={3}
                      />
                    </div>
                    
                    <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Standard
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Add Framework Tab */}
            <TabsContent value="add-framework" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-green-600" />
                    <span>Add New Framework</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleESGSubmit} className="space-y-4">
                    <input type="hidden" value="framework" onChange={(e) => setEsgFormData({...esgFormData, standard_type: 'framework'})} />
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Framework Name *</Label>
                        <Select 
                          value={esgFormData.name} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, name: value, standard_type: 'framework'})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select framework" />
                          </SelectTrigger>
                          <SelectContent>
                            {esgOptions.frameworks?.map(option => (
                              <SelectItem key={option} value={option}>{option}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Submission Year</Label>
                        <Input
                          type="number"
                          min="2020"
                          max="2030"
                          value={esgFormData.submission_year}
                          onChange={(e) => setEsgFormData({...esgFormData, submission_year: e.target.value})}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Score/Rating</Label>
                        <Input
                          value={esgFormData.score_rating}
                          onChange={(e) => setEsgFormData({...esgFormData, score_rating: e.target.value})}
                          placeholder="e.g., A+, 85%, 4.5/5"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Status</Label>
                        <Select 
                          value={esgFormData.status} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, status: value})}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="active">Active</SelectItem>
                            <SelectItem value="expired">Expired</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label>Document Link</Label>
                        <Input
                          type="url"
                          value={esgFormData.document_link}
                          onChange={(e) => setEsgFormData({...esgFormData, document_link: e.target.value})}
                          placeholder="https://..."
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Notes</Label>
                      <Textarea
                        value={esgFormData.notes}
                        onChange={(e) => setEsgFormData({...esgFormData, notes: e.target.value})}
                        placeholder="Additional notes..."
                        rows={3}
                      />
                    </div>
                    
                    <Button type="submit" className="bg-green-600 hover:bg-green-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Framework
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Add Assessment Tab */}
            <TabsContent value="add-assessment" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <ClipboardList className="h-5 w-5 text-purple-600" />
                    <span>Add New Assessment</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleESGSubmit} className="space-y-4">
                    <input type="hidden" value="assessment" onChange={(e) => setEsgFormData({...esgFormData, standard_type: 'assessment'})} />
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Assessment Name *</Label>
                        <Select 
                          value={esgFormData.name} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, name: value, standard_type: 'assessment'})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select assessment" />
                          </SelectTrigger>
                          <SelectContent>
                            {esgOptions.assessments?.map(option => (
                              <SelectItem key={option} value={option}>{option}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Submission Year</Label>
                        <Input
                          type="number"
                          min="2020"
                          max="2030"
                          value={esgFormData.submission_year}
                          onChange={(e) => setEsgFormData({...esgFormData, submission_year: e.target.value})}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Score/Rating</Label>
                        <Input
                          value={esgFormData.score_rating}
                          onChange={(e) => setEsgFormData({...esgFormData, score_rating: e.target.value})}
                          placeholder="e.g., A+, 85%, 4.5/5"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Status</Label>
                        <Select 
                          value={esgFormData.status} 
                          onValueChange={(value) => setEsgFormData({...esgFormData, status: value})}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="active">Active</SelectItem>
                            <SelectItem value="expired">Expired</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label>Document Link</Label>
                        <Input
                          type="url"
                          value={esgFormData.document_link}
                          onChange={(e) => setEsgFormData({...esgFormData, document_link: e.target.value})}
                          placeholder="https://..."
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Notes</Label>
                      <Textarea
                        value={esgFormData.notes}
                        onChange={(e) => setEsgFormData({...esgFormData, notes: e.target.value})}
                        placeholder="Additional notes..."
                        rows={3}
                      />
                    </div>
                    
                    <Button type="submit" className="bg-purple-600 hover:bg-purple-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Assessment
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
}

