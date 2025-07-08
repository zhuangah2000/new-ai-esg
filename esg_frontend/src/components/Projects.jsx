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
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Target, 
  Activity, 
  Calendar, 
  CheckCircle, 
  PlayCircle,
  PauseCircle,
  XCircle,
  Clock,
  User,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Zap,
  Leaf,
  Droplets,
  Trash,
  Building2,
  MapPin,
  Calculator,
  Save,
  X,
  Search,
  Filter,
  FilterX,
  Download,
  FileSpreadsheet,
  Eye,
  ChevronRight,
  ChevronDown,
  Star,
  DollarSign,
  AlertCircle
} from 'lucide-react';

// Safe JSON parsing utility
const safeJsonParse = (jsonString) => {
  if (!jsonString) return [];
  if (Array.isArray(jsonString)) return jsonString;
  
  try {
    const parsed = JSON.parse(jsonString);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch (error) {
    console.warn('Failed to parse JSON, treating as string:', jsonString);
    return typeof jsonString === 'string' ? [jsonString] : [];
  }
};

export function Projects({ apiBaseUrl }) {
  // State management
  const [projects, setProjects] = useState([]);
  const [activities, setActivities] = useState({});
  const [emissionCategories, setEmissionCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dialog states
  const [isProjectDialogOpen, setIsProjectDialogOpen] = useState(false);
  const [isActivityDialogOpen, setIsActivityDialogOpen] = useState(false);
  const [isProgressDialogOpen, setIsProgressDialogOpen] = useState(false);
  
  // Form states
  const [editingProject, setEditingProject] = useState(null);
  const [editingActivity, setEditingActivity] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  
  // Filter states
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [expandedProjects, setExpandedProjects] = useState({});
  
  // Progress tracking states
  const [progressData, setProgressData] = useState(null);
  
  // Form data states
  const [projectFormData, setProjectFormData] = useState({
    name: '',
    description: '',
    year: new Date().getFullYear(),
    start_date: '',
    end_date: '',
    status: 'active',
    target_reduction_percentage: '',
    target_reduction_absolute: '',
    target_reduction_unit: 'kgCO2e',
    baseline_value: '',
    baseline_year: new Date().getFullYear()
  });
  
  const [activityFormData, setActivityFormData] = useState({
    description: '',
    start_date: '',
    due_date: '',
    end_date: '',
    completion_percentage: 0,
    estimated_hours: '',
    actual_hours: '',
    status: 'pending',
    priority: 'medium',
    assigned_to: '',
    depends_on: [],
    blocks: [],
    measurement_ids: [],
    emission_categories: [],
    risk_level: 'low',
    budget_allocated: '',
    budget_spent: '',
    notes: ''
  });

  // Calculate summary statistics
  const summaryStats = React.useMemo(() => {
    const currentYear = new Date().getFullYear();
    const currentYearProjects = projects.filter(p => p.year === currentYear);
    
    const totalProjects = currentYearProjects.length;
    const activeProjects = currentYearProjects.filter(p => p.status === 'active').length;
    const completedProjects = currentYearProjects.filter(p => p.status === 'completed').length;
    const totalActivities = currentYearProjects.reduce((sum, p) => sum + (activities[p.id]?.length || 0), 0);
    
    return {
      totalProjects,
      activeProjects,
      completedProjects,
      totalActivities
    };
  }, [projects, activities]);

  // Filter projects based on search and filter criteria
  const filteredProjects = React.useMemo(() => {
    return projects.filter(project => {
      const matchesSearch = (project.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (project.description || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesYear = yearFilter === 'all' || project.year.toString() === yearFilter;
      const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
      
      // Date range filter
      let matchesDateRange = true;
      if (dateRangeFilter !== 'all') {
        const today = new Date();
        const projectStart = new Date(project.start_date);
        const projectEnd = new Date(project.end_date);
        
        switch (dateRangeFilter) {
          case 'this_month':
            const thisMonth = today.getMonth();
            const thisYear = today.getFullYear();
            matchesDateRange = (projectStart.getMonth() === thisMonth && projectStart.getFullYear() === thisYear) ||
                              (projectEnd.getMonth() === thisMonth && projectEnd.getFullYear() === thisYear);
            break;
          case 'this_quarter':
            const currentQuarter = Math.floor(today.getMonth() / 3);
            const projectStartQuarter = Math.floor(projectStart.getMonth() / 3);
            const projectEndQuarter = Math.floor(projectEnd.getMonth() / 3);
            matchesDateRange = projectStartQuarter === currentQuarter || projectEndQuarter === currentQuarter;
            break;
          case 'overdue':
            matchesDateRange = project.status !== 'completed' && projectEnd < today;
            break;
        }
      }
      
      return matchesSearch && matchesYear && matchesStatus && matchesDateRange;
    });
  }, [projects, searchTerm, yearFilter, statusFilter, dateRangeFilter]);

  // Get unique values for filter options
  const filterOptions = React.useMemo(() => {
    const years = [...new Set(projects.map(p => p.year.toString()).filter(Boolean))].sort().reverse();
    const statuses = [...new Set(projects.map(p => p.status).filter(Boolean))];
    
    return { years, statuses };
  }, [projects]);

  // Fetch data functions
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiBaseUrl}/projects`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setProjects(data.data || []);
        
        // Fetch activities for each project
        const activitiesData = {};
        for (const project of data.data || []) {
          const activitiesResponse = await fetch(`${apiBaseUrl}/projects/${project.id}/activities`);
          if (activitiesResponse.ok) {
            const activitiesResult = await activitiesResponse.json();
            if (activitiesResult.success) {
              activitiesData[project.id] = activitiesResult.data || [];
            }
          }
        }
        setActivities(activitiesData);
      } else {
        throw new Error(data.error || 'Failed to fetch projects');
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
      setError(`Error fetching projects: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmissionCategories = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/emission-categories`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        setEmissionCategories(data.data || []);
      } else {
        throw new Error(data.error || 'Failed to fetch emission categories');
      }
    } catch (error) {
      console.error('Error fetching emission categories:', error);
      setEmissionCategories([]);
    }
  };

  const fetchProgressData = async (projectId) => {
    try {
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/activities`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
      const data = await response.json();
      if (data.success) {
        const projectActivities = data.data || [];
        
        // Calculate progress metrics
        const totalActivities = projectActivities.length;
        const completedActivities = projectActivities.filter(a => a.status === 'completed').length;
        const inProgressActivities = projectActivities.filter(a => a.status === 'in_progress').length;
        const overDueActivities = projectActivities.filter(a => {
          if (!a.due_date) return false;
          const dueDate = new Date(a.due_date);
          const today = new Date();
          return dueDate < today && a.status !== 'completed';
        }).length;
        
        const avgCompletion = totalActivities > 0 
          ? projectActivities.reduce((sum, a) => sum + (a.completion_percentage || 0), 0) / totalActivities 
          : 0;
        
        const totalBudgetAllocated = projectActivities.reduce((sum, a) => sum + (a.budget_allocated || 0), 0);
        const totalBudgetSpent = projectActivities.reduce((sum, a) => sum + (a.budget_spent || 0), 0);
        
        const totalEstimatedHours = projectActivities.reduce((sum, a) => sum + (a.estimated_hours || 0), 0);
        const totalActualHours = projectActivities.reduce((sum, a) => sum + (a.actual_hours || 0), 0);
        
        setProgressData({
          activities: projectActivities,
          metrics: {
            totalActivities,
            completedActivities,
            inProgressActivities,
            overDueActivities,
            avgCompletion: Math.round(avgCompletion),
            totalBudgetAllocated,
            totalBudgetSpent,
            budgetUtilization: totalBudgetAllocated > 0 ? (totalBudgetSpent / totalBudgetAllocated) * 100 : 0,
            totalEstimatedHours,
            totalActualHours,
            timeEfficiency: totalEstimatedHours > 0 ? (totalEstimatedHours / totalActualHours) * 100 : 0
          }
        });
      }
    } catch (error) {
      console.error('Error fetching progress data:', error);
      setError(`Error fetching progress data: ${error.message}`);
    }
  };

  // Initialize data
  useEffect(() => {
    const initializeData = async () => {
      await Promise.all([
        fetchProjects(),
        fetchEmissionCategories()
      ]);
    };
    
    initializeData();
  }, [apiBaseUrl]);

  // Utility functions
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-700 bg-green-50 border-green-200';
      case 'in_progress': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'active': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'on_hold': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'cancelled': return 'text-red-700 bg-red-50 border-red-200';
      case 'pending': return 'text-gray-700 bg-gray-50 border-gray-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'text-red-700 bg-red-50 border-red-200';
      case 'high': return 'text-orange-700 bg-orange-50 border-orange-200';
      case 'medium': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'low': return 'text-gray-700 bg-gray-50 border-gray-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'critical': return 'text-red-700 bg-red-50 border-red-200';
      case 'high': return 'text-orange-700 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-700 bg-green-50 border-green-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'electricity': return <Zap className="h-4 w-4" />;
      case 'fuel': return <Leaf className="h-4 w-4" />;
      case 'water': return <Droplets className="h-4 w-4" />;
      case 'waste': return <Trash className="h-4 w-4" />;
      case 'steam': return <Building2 className="h-4 w-4" />;
      case 'transportation': return <MapPin className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'in_progress': return <PlayCircle className="h-4 w-4" />;
      case 'active': return <PlayCircle className="h-4 w-4" />;
      case 'on_hold': return <PauseCircle className="h-4 w-4" />;
      case 'cancelled': return <XCircle className="h-4 w-4" />;
      case 'pending': return <Clock className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  // Handle tile clicks for filtering
  const handleTileClick = (filterType) => {
    const currentYear = new Date().getFullYear().toString();
    setYearFilter(currentYear);
    
    switch (filterType) {
      case 'total':
        setStatusFilter('all');
        break;
      case 'active':
        setStatusFilter('active');
        break;
      case 'completed':
        setStatusFilter('completed');
        break;
      case 'activities':
        // Toggle activities expansion for all projects
        setStatusFilter('all');
        const allExpanded = Object.keys(expandedProjects).length === filteredProjects.length;
        if (allExpanded) {
          setExpandedProjects({});
        } else {
          const newExpanded = {};
          filteredProjects.forEach(p => newExpanded[p.id] = true);
          setExpandedProjects(newExpanded);
        }
        break;
    }
  };

  // Clear filters function
  const clearFilters = () => {
    setSearchTerm('');
    setYearFilter('all');
    setStatusFilter('all');
    setDateRangeFilter('all');
  };

  // Project CRUD operations
  const resetProjectForm = () => {
    setProjectFormData({
      name: '',
      description: '',
      year: new Date().getFullYear(),
      start_date: '',
      end_date: '',
      status: 'active',
      target_reduction_percentage: '',
      target_reduction_absolute: '',
      target_reduction_unit: 'kgCO2e',
      baseline_value: '',
      baseline_year: new Date().getFullYear()
    });
  };

  const resetActivityForm = () => {
    setActivityFormData({
      description: '',
      start_date: '',
      due_date: '',
      end_date: '',
      completion_percentage: 0,
      estimated_hours: '',
      actual_hours: '',
      status: 'pending',
      priority: 'medium',
      assigned_to: '',
      depends_on: [],
      blocks: [],
      measurement_ids: [],
      emission_categories: [],
      risk_level: 'low',
      budget_allocated: '',
      budget_spent: '',
      notes: ''
    });
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingProject 
        ? `${apiBaseUrl}/projects/${editingProject.id}`
        : `${apiBaseUrl}/projects`;
      
      const method = editingProject ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectFormData),
      });
      
      if (response.ok) {
        await fetchProjects();
        setIsProjectDialogOpen(false);
        setEditingProject(null);
        resetProjectForm();
        setError(null);
      } else {
        throw new Error('Failed to save project');
      }
    } catch (error) {
      console.error('Error saving project:', error);
      setError('Failed to save project. Please try again.');
    }
  };

  const handleActivitySubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingActivity 
        ? `${apiBaseUrl}/projects/${selectedProject.id}/activities/${editingActivity.id}`
        : `${apiBaseUrl}/projects/${selectedProject.id}/activities`;
      
      const method = editingActivity ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(activityFormData),
      });
      
      if (response.ok) {
        await fetchProjects();
        setIsActivityDialogOpen(false);
        setEditingActivity(null);
        resetActivityForm();
        setError(null);
      } else {
        throw new Error('Failed to save activity');
      }
    } catch (error) {
      console.error('Error saving activity:', error);
      setError('Failed to save activity. Please try again.');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchProjects();
        setError(null);
      } else {
        throw new Error('Failed to delete project');
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      setError('Failed to delete project. Please try again.');
    }
  };

  const handleDeleteActivity = async (projectId, activityId) => {
    if (!confirm('Are you sure you want to delete this activity?')) return;
    
    try {
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/activities/${activityId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchProjects();
        setError(null);
      } else {
        throw new Error('Failed to delete activity');
      }
    } catch (error) {
      console.error('Error deleting activity:', error);
      setError('Failed to delete activity. Please try again.');
    }
  };

  // Export functions
  const exportProjects = () => {
    const headers = [
      'Project ID', 'Project Name', 'Description', 'Year', 'Start Date', 'End Date', 'Status',
      'Target Reduction %', 'Target Reduction Absolute', 'Target Unit', 'Baseline Value', 'Baseline Year'
    ];
    
    const csvData = filteredProjects.map(project => [
      project.id,
      project.name || '',
      project.description || '',
      project.year,
      project.start_date || '',
      project.end_date || '',
      project.status,
      project.target_reduction_percentage || '',
      project.target_reduction_absolute || '',
      project.target_reduction_unit || '',
      project.baseline_value || '',
      project.baseline_year || ''
    ]);
    
    downloadCSV([headers, ...csvData], `projects_export_${new Date().toISOString().split('T')[0]}.csv`);
  };

  const exportProjectsWithActivities = () => {
    const headers = [
      'Project ID', 'Project Name', 'Project Status', 'Activity ID', 'Activity Description',
      'Activity Status', 'Start Date', 'Due Date', 'End Date', 'Completion %', 'Assigned To',
      'Priority', 'Risk Level', 'Budget Allocated', 'Budget Spent', 'Estimated Hours',
      'Actual Hours', 'Emission Factors', 'Notes'
    ];
    
    const csvData = [];
    
    filteredProjects.forEach(project => {
      const projectActivities = activities[project.id] || [];
      
      if (projectActivities.length === 0) {
        csvData.push([
          project.id, project.name, project.status, '', 'No activities',
          '', '', '', '', '', '', '', '', '', '', '', '', '', ''
        ]);
      } else {
        projectActivities.forEach(activity => {
          const selectedFactorIds = activity.measurement_ids ? 
            safeJsonParse(activity.measurement_ids) : [];
          
          const selectedFactors = selectedFactorIds.map(id => {
            return emissionCategories
              .flatMap(cat => cat.factors || [])
              .find(f => f.id === id);
          }).filter(Boolean);
          
          const emissionFactorNames = selectedFactors.map(f => f.name).join('; ');
          
          csvData.push([
            project.id,
            project.name,
            project.status,
            activity.id,
            activity.description,
            activity.status,
            activity.start_date || '',
            activity.due_date || '',
            activity.end_date || '',
            activity.completion_percentage || 0,
            activity.assigned_to || '',
            activity.priority || '',
            activity.risk_level || '',
            activity.budget_allocated || '',
            activity.budget_spent || '',
            activity.estimated_hours || '',
            activity.actual_hours || '',
            emissionFactorNames,
            activity.notes || ''
          ]);
        });
      }
    });
    
    downloadCSV([headers, ...csvData], `projects_with_activities_${new Date().toISOString().split('T')[0]}.csv`);
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

  // Progress tracking dialog functions
  const openProgressDialog = async (project) => {
    setSelectedProject(project);
    setIsProgressDialogOpen(true);
    await fetchProgressData(project.id);
  };

  const closeProgressDialog = () => {
    setIsProgressDialogOpen(false);
    setSelectedProject(null);
    setProgressData(null);
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
          <h1 className="text-3xl font-bold text-gray-900">Project Management</h1>
          <p className="text-gray-600 mt-1">Manage your ESG projects and track their progress</p>
        </div>
        <Dialog open={isProjectDialogOpen} onOpenChange={setIsProjectDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              onClick={() => {
                setEditingProject(null);
                resetProjectForm();
              }}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Project
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingProject ? 'Edit Project' : 'Add New Project'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleProjectSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={projectFormData.name}
                    onChange={(e) => setProjectFormData({...projectFormData, name: e.target.value})}
                    placeholder="Enter project name"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="year">Year</Label>
                  <Input
                    id="year"
                    type="number"
                    value={projectFormData.year}
                    onChange={(e) => setProjectFormData({...projectFormData, year: parseInt(e.target.value)})}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={projectFormData.status} onValueChange={(value) => setProjectFormData({...projectFormData, status: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="on_hold">On Hold</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={projectFormData.start_date}
                    onChange={(e) => setProjectFormData({...projectFormData, start_date: e.target.value})}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={projectFormData.end_date}
                    onChange={(e) => setProjectFormData({...projectFormData, end_date: e.target.value})}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="target_reduction_percentage">Target Reduction %</Label>
                  <Input
                    id="target_reduction_percentage"
                    type="number"
                    step="0.1"
                    value={projectFormData.target_reduction_percentage}
                    onChange={(e) => setProjectFormData({...projectFormData, target_reduction_percentage: e.target.value})}
                    placeholder="e.g., 20.5"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="target_reduction_absolute">Target Reduction Absolute</Label>
                  <Input
                    id="target_reduction_absolute"
                    type="number"
                    value={projectFormData.target_reduction_absolute}
                    onChange={(e) => setProjectFormData({...projectFormData, target_reduction_absolute: e.target.value})}
                    placeholder="e.g., 1000"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="target_reduction_unit">Target Unit</Label>
                  <Select value={projectFormData.target_reduction_unit} onValueChange={(value) => setProjectFormData({...projectFormData, target_reduction_unit: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select unit" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="kgCO2e">kgCO2e</SelectItem>
                      <SelectItem value="tCO2e">tCO2e</SelectItem>
                      <SelectItem value="kWh">kWh</SelectItem>
                      <SelectItem value="MWh">MWh</SelectItem>
                      <SelectItem value="%">%</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="baseline_value">Baseline Value</Label>
                  <Input
                    id="baseline_value"
                    type="number"
                    value={projectFormData.baseline_value}
                    onChange={(e) => setProjectFormData({...projectFormData, baseline_value: e.target.value})}
                    placeholder="Starting point for reduction"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={projectFormData.description}
                  onChange={(e) => setProjectFormData({...projectFormData, description: e.target.value})}
                  placeholder="Enter project description"
                  rows={3}
                />
              </div>
              
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsProjectDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                  {editingProject ? 'Update' : 'Create'} Project
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
          <TabsTrigger value="overview">Project Overview</TabsTrigger>
          <TabsTrigger value="tracking">Progress Tracking</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card 
              className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('total')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-emerald-800">Total Projects</CardTitle>
                <Target className="h-4 w-4 text-emerald-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-900">{summaryStats.totalProjects}</div>
                <p className="text-xs text-emerald-600 mt-1">This year</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('active')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-800">Active Projects</CardTitle>
                <PlayCircle className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{summaryStats.activeProjects}</div>
                <p className="text-xs text-blue-600 mt-1">Currently running</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-green-50 to-green-100 border-green-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('completed')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-800">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">{summaryStats.completedProjects}</div>
                <p className="text-xs text-green-600 mt-1">Successfully finished</p>
              </CardContent>
            </Card>

            <Card 
              className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200 cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              onClick={() => handleTileClick('activities')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-amber-800">Total Activities</CardTitle>
                <Activity className="h-4 w-4 text-amber-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-900">{summaryStats.totalActivities}</div>
                <p className="text-xs text-amber-600 mt-1">All project tasks</p>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-semibold text-gray-800">Search & Filter Projects</CardTitle>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={exportProjects}
                    className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export Projects
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={exportProjectsWithActivities}
                    className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                  >
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Export with Activities
                  </Button>
                  {(searchTerm || yearFilter !== 'all' || statusFilter !== 'all' || dateRangeFilter !== 'all') && (
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
                  placeholder="Search projects by name or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full"
                />
              </div>
              
              {/* Filter Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Year</Label>
                  <Select value={yearFilter} onValueChange={setYearFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Years" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Years</SelectItem>
                      {filterOptions.years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
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
                  <Label>Date Range</Label>
                  <Select value={dateRangeFilter} onValueChange={setDateRangeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Time" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Time</SelectItem>
                      <SelectItem value="this_month">This Month</SelectItem>
                      <SelectItem value="this_quarter">This Quarter</SelectItem>
                      <SelectItem value="overdue">Overdue</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              {/* Active Filters Display */}
              {(searchTerm || yearFilter !== 'all' || statusFilter !== 'all' || dateRangeFilter !== 'all') && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {searchTerm && (
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                      Search: "{searchTerm}"
                    </Badge>
                  )}
                  {yearFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Year: {yearFilter}
                    </Badge>
                  )}
                  {statusFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-amber-100 text-amber-800">
                      Status: {statusFilter}
                    </Badge>
                  )}
                  {dateRangeFilter !== 'all' && (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Range: {dateRangeFilter.replace('_', ' ')}
                    </Badge>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Projects Table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Projects ({filteredProjects.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredProjects.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Target className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
                    <p className="text-gray-500">No projects match your current search criteria.</p>
                  </div>
                ) : (
                  filteredProjects.map((project) => {
                    const projectActivities = activities[project.id] || [];
                    const completedActivities = projectActivities.filter(a => a.status === 'completed').length;
                    const totalActivitiesCount = projectActivities.length;
                    const progressPercentage = totalActivitiesCount > 0 ? Math.round((completedActivities / totalActivitiesCount) * 100) : 0;
                    const isExpanded = expandedProjects[project.id];
                    
                    return (
                      <Card key={project.id} className="border border-gray-200 hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="text-xl font-semibold text-gray-900">{project.name}</h3>
                                <Badge className={`${getStatusColor(project.status)} border`}>
                                  {getStatusIcon(project.status)}
                                  <span className="ml-1">{project.status}</span>
                                </Badge>
                                <Badge variant="outline" className="text-gray-600">
                                  Year {project.year}
                                </Badge>
                              </div>
                              
                              {project.description && (
                                <p className="text-gray-600 mb-4">{project.description}</p>
                              )}
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                                <div className="flex items-center space-x-2 text-sm text-gray-600">
                                  <Calendar className="h-4 w-4" />
                                  <span>{formatDate(project.start_date)} - {formatDate(project.end_date)}</span>
                                </div>
                                
                                <div className="flex items-center space-x-2 text-sm text-gray-600">
                                  <Activity className="h-4 w-4" />
                                  <span>{totalActivitiesCount} activities ({completedActivities} completed)</span>
                                </div>
                                
                                {project.target_reduction_percentage && (
                                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                                    <TrendingUp className="h-4 w-4" />
                                    <span>Target: {project.target_reduction_percentage}% reduction</span>
                                  </div>
                                )}
                              </div>
                              
                              {/* Progress Bar */}
                              <div className="mb-4">
                                <div className="flex items-center justify-between text-sm mb-2">
                                  <span className="font-medium">Project Progress</span>
                                  <span>{progressPercentage}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className={`h-2 rounded-full ${
                                      progressPercentage === 100 ? 'bg-green-500' : 
                                      progressPercentage > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                                    }`}
                                    style={{ width: `${progressPercentage}%` }}
                                  ></div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex space-x-2 ml-6">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => openProgressDialog(project)}
                                className="text-purple-600 hover:text-purple-700 hover:bg-purple-50 border-purple-200"
                                title="Track Progress"
                              >
                                <BarChart3 className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setEditingProject(project);
                                  setProjectFormData({
                                    name: project.name,
                                    description: project.description || '',
                                    year: project.year,
                                    start_date: project.start_date,
                                    end_date: project.end_date,
                                    status: project.status,
                                    target_reduction_percentage: project.target_reduction_percentage || '',
                                    target_reduction_absolute: project.target_reduction_absolute || '',
                                    target_reduction_unit: project.target_reduction_unit || 'kgCO2e',
                                    baseline_value: project.baseline_value || '',
                                    baseline_year: project.baseline_year || new Date().getFullYear()
                                  });
                                  setIsProjectDialogOpen(true);
                                }}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
                                title="Edit Project"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteProject(project.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                                title="Delete Project"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                          
                          {/* Project Activities Overview */}
                          {projectActivities.length > 0 && (
                            <div className="border-t pt-4">
                              <div className="flex items-center justify-between mb-3">
                                <button
                                  onClick={() => setExpandedProjects(prev => ({
                                    ...prev,
                                    [project.id]: !prev[project.id]
                                  }))}
                                  className="flex items-center space-x-2 text-gray-900 hover:text-blue-600"
                                >
                                  {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                                  <h4 className="font-medium">Activities ({projectActivities.length})</h4>
                                </button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedProject(project);
                                    setEditingActivity(null);
                                    resetActivityForm();
                                    setIsActivityDialogOpen(true);
                                  }}
                                  className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 border-emerald-200"
                                >
                                  <Plus className="h-3 w-3 mr-1" />
                                  Add Activity
                                </Button>
                              </div>
                              
                              {isExpanded && (
                                <div className="space-y-2">
                                  {projectActivities.map((activity) => {
                                    const selectedFactorIds = activity.measurement_ids ? 
                                      safeJsonParse(activity.measurement_ids) : [];
                                    
                                    // Get emission factor details for display
                                    const selectedFactors = selectedFactorIds.map(id => {
                                      return emissionCategories
                                        .flatMap(cat => cat.factors || [])
                                        .find(f => f.id === id);
                                    }).filter(Boolean);
                                    
                                    return (
                                      <div key={activity.id} className="bg-gray-50 rounded p-3">
                                        <div className="flex items-start justify-between">
                                          <div className="flex-1">
                                            <div className="flex items-center space-x-2 mb-2">
                                              <p className="font-medium text-gray-900">{activity.description}</p>
                                              <Badge className={`${getStatusColor(activity.status)} border text-xs`}>
                                                {activity.status}
                                              </Badge>
                                              <Badge className={`${getPriorityColor(activity.priority)} border text-xs`}>
                                                {activity.priority}
                                              </Badge>
                                              {activity.risk_level && activity.risk_level !== 'low' && (
                                                <Badge className={`${getRiskColor(activity.risk_level)} border text-xs`}>
                                                  <AlertTriangle className="h-3 w-3 mr-1" />
                                                  {activity.risk_level} risk
                                                </Badge>
                                              )}
                                            </div>
                                            
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600">
                                              {activity.start_date && (
                                                <div className="flex items-center space-x-1">
                                                  <PlayCircle className="h-3 w-3" />
                                                  <span>Start: {formatDate(activity.start_date)}</span>
                                                </div>
                                              )}
                                              
                                              {activity.due_date && (
                                                <div className="flex items-center space-x-1">
                                                  <Calendar className="h-3 w-3" />
                                                  <span>Due: {formatDate(activity.due_date)}</span>
                                                </div>
                                              )}
                                              
                                              {activity.assigned_to && (
                                                <div className="flex items-center space-x-1">
                                                  <User className="h-3 w-3" />
                                                  <span>{activity.assigned_to}</span>
                                                </div>
                                              )}
                                            </div>
                                            
                                            {/* Display selected emission factors */}
                                            {selectedFactors.length > 0 && (
                                              <div className="mt-2">
                                                <div className="flex flex-wrap gap-1">
                                                  {selectedFactors.map((factor, idx) => (
                                                    <Badge key={idx} variant="outline" className="text-xs">
                                                      <span className="font-medium">{factor.name}</span>
                                                      <span className="text-gray-500 ml-1">
                                                        ({factor.factor_value} {factor.unit})
                                                      </span>
                                                    </Badge>
                                                  ))}
                                                </div>
                                              </div>
                                            )}
                                            
                                            {/* Progress bar for activity */}
                                            <div className="mt-2">
                                              <div className="flex items-center justify-between text-xs mb-1">
                                                <span>Progress</span>
                                                <span>{activity.completion_percentage || 0}%</span>
                                              </div>
                                              <div className="w-full bg-gray-200 rounded-full h-1">
                                                <div 
                                                  className={`h-1 rounded-full ${
                                                    (activity.completion_percentage || 0) === 100 ? 'bg-green-500' : 
                                                    (activity.completion_percentage || 0) > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                                                  }`}
                                                  style={{ width: `${activity.completion_percentage || 0}%` }}
                                                ></div>
                                              </div>
                                            </div>
                                            
                                            {activity.notes && (
                                              <p className="text-sm text-gray-500 mt-2">{activity.notes}</p>
                                            )}
                                          </div>
                                          
                                          <div className="flex space-x-1 ml-4">
                                            <Button
                                              variant="outline"
                                              size="sm"
                                              onClick={() => {
                                                setSelectedProject(project);
                                                setEditingActivity(activity);
                                                setActivityFormData({
                                                  description: activity.description,
                                                  start_date: activity.start_date || '',
                                                  due_date: activity.due_date || '',
                                                  end_date: activity.end_date || '',
                                                  completion_percentage: activity.completion_percentage || 0,
                                                  estimated_hours: activity.estimated_hours || '',
                                                  actual_hours: activity.actual_hours || '',
                                                  status: activity.status,
                                                  priority: activity.priority,
                                                  assigned_to: activity.assigned_to || '',
                                                  depends_on: safeJsonParse(activity.depends_on),
                                                  blocks: safeJsonParse(activity.blocks),
                                                  measurement_ids: safeJsonParse(activity.measurement_ids),
                                                  emission_categories: safeJsonParse(activity.emission_categories),
                                                  risk_level: activity.risk_level || 'low',
                                                  budget_allocated: activity.budget_allocated || '',
                                                  budget_spent: activity.budget_spent || '',
                                                  notes: activity.notes || ''
                                                });
                                                setIsActivityDialogOpen(true);
                                              }}
                                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
                                              title="Edit Activity"
                                            >
                                              <Edit className="h-3 w-3" />
                                            </Button>
                                            <Button
                                              variant="outline"
                                              size="sm"
                                              onClick={() => handleDeleteActivity(project.id, activity.id)}
                                              className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                                              title="Delete Activity"
                                            >
                                              <Trash2 className="h-3 w-3" />
                                            </Button>
                                          </div>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tracking" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Progress Tracking Dashboard</CardTitle>
              <p className="text-sm text-gray-600">Monitor project progress and performance metrics</p>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-gray-500">
                <BarChart3 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a project to track progress</h3>
                <p className="text-gray-500">Use the "Track Progress" button on any project to view detailed analytics.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Activity Dialog */}
      <Dialog open={isActivityDialogOpen} onOpenChange={setIsActivityDialogOpen}>
        <DialogContent className="w-[85vw] sm:max-w-[85vw] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingActivity ? 'Edit Activity' : 'Add New Activity'} - {selectedProject?.name}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleActivitySubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-2 md:col-span-3">
                <Label htmlFor="description">Activity Description</Label>
                <Textarea
                  id="description"
                  value={activityFormData.description}
                  onChange={(e) => setActivityFormData({...activityFormData, description: e.target.value})}
                  placeholder="Describe the activity"
                  rows={3}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={activityFormData.start_date}
                  onChange={(e) => setActivityFormData({...activityFormData, start_date: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={activityFormData.due_date}
                  onChange={(e) => setActivityFormData({...activityFormData, due_date: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={activityFormData.end_date}
                  onChange={(e) => setActivityFormData({...activityFormData, end_date: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select value={activityFormData.status} onValueChange={(value) => setActivityFormData({...activityFormData, status: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="on_hold">On Hold</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={activityFormData.priority} onValueChange={(value) => setActivityFormData({...activityFormData, priority: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="assigned_to">Assigned To</Label>
                <Input
                  id="assigned_to"
                  value={activityFormData.assigned_to}
                  onChange={(e) => setActivityFormData({...activityFormData, assigned_to: e.target.value})}
                  placeholder="Person responsible"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="risk_level">Risk Level</Label>
                <Select value={activityFormData.risk_level} onValueChange={(value) => setActivityFormData({...activityFormData, risk_level: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select risk level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="estimated_hours">Estimated Hours</Label>
                <Input
                  id="estimated_hours"
                  type="number"
                  step="0.5"
                  value={activityFormData.estimated_hours}
                  onChange={(e) => setActivityFormData({...activityFormData, estimated_hours: e.target.value})}
                  placeholder="Planned effort"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="actual_hours">Actual Hours</Label>
                <Input
                  id="actual_hours"
                  type="number"
                  step="0.5"
                  value={activityFormData.actual_hours}
                  onChange={(e) => setActivityFormData({...activityFormData, actual_hours: e.target.value})}
                  placeholder="Actual effort"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="budget_allocated">Budget Allocated</Label>
                <Input
                  id="budget_allocated"
                  type="number"
                  step="0.01"
                  value={activityFormData.budget_allocated}
                  onChange={(e) => setActivityFormData({...activityFormData, budget_allocated: e.target.value})}
                  placeholder="Budget assigned"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="budget_spent">Budget Spent</Label>
                <Input
                  id="budget_spent"
                  type="number"
                  step="0.01"
                  value={activityFormData.budget_spent}
                  onChange={(e) => setActivityFormData({...activityFormData, budget_spent: e.target.value})}
                  placeholder="Budget used"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="completion_percentage">Completion Percentage</Label>
              <div className="flex items-center space-x-4">
                <Input
                  id="completion_percentage"
                  type="range"
                  min="0"
                  max="100"
                  value={activityFormData.completion_percentage}
                  onChange={(e) => setActivityFormData({...activityFormData, completion_percentage: parseInt(e.target.value)})}
                  className="flex-1"
                />
                <span className="text-sm font-medium w-12">{activityFormData.completion_percentage}%</span>
              </div>
            </div>
            
            {/* Emission Categories Selection */}
            <div className="space-y-2">
              <Label>Emission Categories</Label>
              <div className="space-y-2 max-h-40 overflow-y-auto border rounded-lg p-3">
                {emissionCategories.map((category) => (
                  <div key={category.name}>
                    <div className="flex items-center space-x-2 mb-2">
                      {getCategoryIcon(category.name)}
                      <span className="font-medium">{category.label}</span>
                      <span className="text-sm text-gray-500">({category.factors?.length || 0} factors)</span>
                    </div>
                    
                    <div className="ml-6 space-y-1">
                      {(category.factors || []).map((factor) => (
                        <label key={factor.id} className="flex items-center space-x-2 text-sm">
                          <Checkbox
                            checked={activityFormData.measurement_ids.includes(factor.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setActivityFormData(prev => ({
                                  ...prev,
                                  measurement_ids: [...prev.measurement_ids, factor.id]
                                }));
                              } else {
                                setActivityFormData(prev => ({
                                  ...prev,
                                  measurement_ids: prev.measurement_ids.filter(id => id !== factor.id)
                                }));
                              }
                            }}
                          />
                          <span>{factor.name}</span>
                          <span className="text-gray-500">({factor.factor_value} {factor.unit})</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={activityFormData.notes}
                onChange={(e) => setActivityFormData({...activityFormData, notes: e.target.value})}
                placeholder="Additional notes and updates"
                rows={3}
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsActivityDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                {editingActivity ? 'Update' : 'Create'} Activity
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Progress Tracking Dialog */}
      <Dialog open={isProgressDialogOpen} onOpenChange={setIsProgressDialogOpen}>
        <DialogContent className="w-[90vw] sm:max-w-[90vw] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">
              Project Progress - {selectedProject?.name}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {progressData ? (
              <>
                {/* Progress Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-blue-800">Total Activities</CardTitle>
                      <Activity className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-blue-900">{progressData.metrics.totalActivities}</div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-green-800">Completed</CardTitle>
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-green-900">{progressData.metrics.completedActivities}</div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-yellow-800">In Progress</CardTitle>
                      <PlayCircle className="h-4 w-4 text-yellow-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-yellow-900">{progressData.metrics.inProgressActivities}</div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-red-800">Overdue</CardTitle>
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-red-900">{progressData.metrics.overDueActivities}</div>
                    </CardContent>
                  </Card>
                </div>
                
                {/* Overall Progress */}
                <Card>
                  <CardHeader>
                    <CardTitle>Overall Progress</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span>Average Completion</span>
                      <span>{progressData.metrics.avgCompletion}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full ${
                          progressData.metrics.avgCompletion === 100 ? 'bg-green-500' : 
                          progressData.metrics.avgCompletion > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${progressData.metrics.avgCompletion}%` }}
                      ></div>
                    </div>
                  </CardContent>
                </Card>
                
                {/* Activities List */}
                <Card>
                  <CardHeader>
                    <CardTitle>Activity Details</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {progressData.activities.map((activity) => (
                        <div key={activity.id} className="border rounded-lg p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h5 className="font-medium">{activity.description}</h5>
                                <Badge className={`${getStatusColor(activity.status)} border`}>
                                  {getStatusIcon(activity.status)}
                                  <span className="ml-1">{activity.status}</span>
                                </Badge>
                                <Badge className={`${getPriorityColor(activity.priority)} border`}>
                                  {activity.priority}
                                </Badge>
                                {activity.risk_level && activity.risk_level !== 'low' && (
                                  <Badge className={`${getRiskColor(activity.risk_level)} border`}>
                                    <AlertTriangle className="h-3 w-3 mr-1" />
                                    {activity.risk_level} risk
                                  </Badge>
                                )}
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                                {activity.start_date && (
                                  <div className="flex items-center space-x-1">
                                    <PlayCircle className="h-3 w-3" />
                                    <span>Start: {formatDate(activity.start_date)}</span>
                                  </div>
                                )}
                                {activity.due_date && (
                                  <div className="flex items-center space-x-1">
                                    <Calendar className="h-3 w-3" />
                                    <span>Due: {formatDate(activity.due_date)}</span>
                                  </div>
                                )}
                                {activity.end_date && (
                                  <div className="flex items-center space-x-1">
                                    <CheckCircle className="h-3 w-3" />
                                    <span>End: {formatDate(activity.end_date)}</span>
                                  </div>
                                )}
                                {activity.assigned_to && (
                                  <div className="flex items-center space-x-1">
                                    <User className="h-3 w-3" />
                                    <span>{activity.assigned_to}</span>
                                  </div>
                                )}
                              </div>
                              
                              {/* Progress bar */}
                              <div className="mb-3">
                                <div className="flex items-center justify-between text-sm mb-1">
                                  <span>Progress</span>
                                  <span>{activity.completion_percentage || 0}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className={`h-2 rounded-full ${
                                      (activity.completion_percentage || 0) === 100 ? 'bg-green-500' : 
                                      (activity.completion_percentage || 0) > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                                    }`}
                                    style={{ width: `${activity.completion_percentage || 0}%` }}
                                  ></div>
                                </div>
                              </div>
                              
                              {/* Budget and time tracking */}
                              {(activity.budget_allocated || activity.estimated_hours) && (
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                  {activity.budget_allocated && (
                                    <div className="bg-gray-50 p-2 rounded">
                                      <div className="font-medium">Budget</div>
                                      <div className="text-gray-600">
                                        ${activity.budget_spent || 0} / ${activity.budget_allocated}
                                      </div>
                                      <div className="text-xs text-gray-500">
                                        {activity.budget_allocated > 0 
                                          ? Math.round(((activity.budget_spent || 0) / activity.budget_allocated) * 100)
                                          : 0}% utilized
                                      </div>
                                    </div>
                                  )}
                                  {activity.estimated_hours && (
                                    <div className="bg-gray-50 p-2 rounded">
                                      <div className="font-medium">Time</div>
                                      <div className="text-gray-600">
                                        {activity.actual_hours || 0}h / {activity.estimated_hours}h
                                      </div>
                                      <div className="text-xs text-gray-500">
                                        {activity.estimated_hours > 0 
                                          ? Math.round(((activity.actual_hours || 0) / activity.estimated_hours) * 100)
                                          : 0}% of estimate
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {activity.notes && (
                                <div className="mt-3 p-2 bg-blue-50 rounded text-sm">
                                  <div className="font-medium text-blue-800 mb-1">Notes</div>
                                  <div className="text-blue-700">{activity.notes}</div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
                <span className="ml-2">Loading progress data...</span>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

