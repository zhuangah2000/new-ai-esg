import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon, Building2, User, Shield, Key, Bell, Database,
  Save, Edit, Trash2, Plus, Eye, EyeOff, Copy, Check,
  AlertCircle, CheckCircle, XCircle, Clock, Users,
  Globe, Calendar, DollarSign, Palette, Mail, Phone,
  MapPin, FileText, Target, Activity, BarChart3, Zap,
  FolderOpen, HardDrive, ChevronDown, ChevronRight,
  RefreshCw, Download, Upload, X
} from 'lucide-react';

export const Settings = ({ apiBaseUrl }) => {
  // State management
  const [activeTab, setActiveTab] = useState('company');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Company state
  const [company, setCompany] = useState({
    name: '',
    legal_name: '',
    industry: '',
    description: '',
    website: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    tax_id: '',
    registration_number: '',
    reporting_year: new Date().getFullYear(),
    fiscal_year_start: '01-01',
    fiscal_year_end: '12-31',
    currency: 'USD',
    timezone: 'UTC',
    reporting_frameworks: [],
    materiality_topics: [],
    logo_url: '',
    primary_color: '#10b981',
    secondary_color: '#3b82f6'
  });

  // User state
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    department: '',
    job_title: '',
    role_id: 4,
    is_active: true
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // Role state
  const [roles, setRoles] = useState([]);
  const [roleFormData, setRoleFormData] = useState({
    name: '',
    description: '',
    color: '#6b7280',
    permissions: {}
  });
  const [showRoleDialog, setShowRoleDialog] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  // FIXED: Updated permission modules to match database schema
  const [permissionModules] = useState([
    'dashboard', 'emission_factors', 'measurements', 'suppliers', 
    'projects', 'esg_targets', 'assets', 'reports', 'settings',
    'company', 'users', 'roles', 'api_keys'  // Added these four modules
  ]);

  // ENHANCED: API Key state with proper key management
  const [apiKeys, setApiKeys] = useState([]);
  const [apiKeyFormData, setApiKeyFormData] = useState({
    name: '',
    description: '',
    permissions: {},
    allowed_ips: [],
    rate_limit: 1000,
    expires_days: 365
  });
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [editingApiKey, setEditingApiKey] = useState(null);
  const [newApiKey, setNewApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  
  // FIXED: Enhanced state for managing key visibility and copy status
  const [visibleKeys, setVisibleKeys] = useState(new Set());
  const [copiedKeys, setCopiedKeys] = useState(new Set());
  // NEW: Store full keys temporarily for copy/display functionality
  const [fullKeys, setFullKeys] = useState(new Map()); // Map<keyId, fullKey>

  // Available options
  const [frameworks, setFrameworks] = useState([]);
  const [materialityTopics, setMaterialityTopics] = useState([]);

  // ENHANCED: Unified API call function with settings permission fallback
  const makeSettingsApiCall = async (endpoint, options = {}) => {
    const { 
      method = 'GET', 
      body = null, 
      headers = {},
      useSettingsEndpoint = false 
    } = options;

    try {
      // First, try the original endpoint
      let url = `${apiBaseUrl}${endpoint}`;
      
      // If useSettingsEndpoint is true, try settings-based endpoint first
      if (useSettingsEndpoint) {
        url = `${apiBaseUrl}/settings${endpoint}`;
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        credentials: 'include',
        body: body ? JSON.stringify(body) : null
      });

      // If original endpoint fails with 403 and we haven't tried settings endpoint yet
      if (response.status === 403 && !useSettingsEndpoint) {
        console.log(`Access denied to ${endpoint}, trying settings-based endpoint...`);
        
        // Try with settings-based endpoint
        const settingsUrl = `${apiBaseUrl}/settings${endpoint}`;
        const settingsResponse = await fetch(settingsUrl, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...headers
          },
          credentials: 'include',
          body: body ? JSON.stringify(body) : null
        });

        return settingsResponse;
      }

      return response;
    } catch (error) {
      console.error(`Error making API call to ${endpoint}:`, error);
      throw error;
    }
  };

  // FIXED: Helper function to create default permissions structure with all modules
  const createDefaultPermissions = () => {
    const permissions = {};
    permissionModules.forEach(module => {
      permissions[module] = {
        read: false,
        write: false,
        delete: false
      };
    });
    return permissions;
  };

  // FIXED: Helper function to create full permissions for API keys
  const createFullPermissions = () => {
    const permissions = {};
    permissionModules.forEach(module => {
      permissions[module] = {
        read: true,
        write: true,
        delete: true
      };
    });
    return permissions;
  };

  // FIXED: Helper function to ensure permissions have all modules
  const ensureCompletePermissions = (permissions) => {
    const completePermissions = createDefaultPermissions();
    
    // Merge existing permissions with defaults
    permissionModules.forEach(module => {
      if (permissions && permissions[module]) {
        completePermissions[module] = {
          read: permissions[module].read || false,
          write: permissions[module].write || false,
          delete: permissions[module].delete || false
        };
      }
    });
    
    return completePermissions;
  };

  // FIXED: Enhanced API key visibility and copy functions
  const toggleKeyVisibility = (keyId) => {
    setVisibleKeys(prev => {
      const newSet = new Set(prev);
      if (newSet.has(keyId)) {
        newSet.delete(keyId);
      } else {
        newSet.add(keyId);
      }
      return newSet;
    });
  };

  // FIXED: Enhanced copy function with proper full key handling
  const copyApiKey = async (keyId) => {
    try {
      // Get the full key from our stored map
      const fullKey = fullKeys.get(keyId);
      
      if (!fullKey) {
        // If no full key available, get the API key from the list and use prefix
        const apiKey = apiKeys.find(key => key.id === keyId);
        if (apiKey && apiKey.key_prefix) {
          showMessage('Only partial key available. Full key is only shown once for security.', 'error');
          return;
        } else {
          showMessage('No API key available to copy', 'error');
          return;
        }
      }

      await navigator.clipboard.writeText(fullKey);
      setCopiedKeys(prev => new Set(prev).add(keyId));
      showMessage('Full API key copied to clipboard');
      
      // Reset copy status after 2 seconds
      setTimeout(() => {
        setCopiedKeys(prev => {
          const newSet = new Set(prev);
          newSet.delete(keyId);
          return newSet;
        });
      }, 2000);
    } catch (error) {
      console.error('Failed to copy API key:', error);
      showMessage('Failed to copy API key', 'error');
    }
  };

  // FIXED: Enhanced copy function for new API key dialog
  const copyNewApiKey = async () => {
    try {
      if (!newApiKey) {
        showMessage('No API key to copy', 'error');
        return;
      }

      await navigator.clipboard.writeText(newApiKey);
      showMessage('API key copied to clipboard');
    } catch (error) {
      console.error('Failed to copy new API key:', error);
      showMessage('Failed to copy API key', 'error');
    }
  };

  // FIXED: Enhanced format API key function
  const formatApiKey = (keyId, keyPrefix, isVisible) => {
    if (isVisible) {
      const fullKey = fullKeys.get(keyId);
      if (fullKey) {
        return fullKey;
      }
    }
    return keyPrefix || 'Key not available';
  };

  // Utility functions
  const showMessage = (message, type = 'success') => {
    if (type === 'success') {
      setSuccess(message);
      setError('');
    } else {
      setError(message);
      setSuccess('');
    }
    setTimeout(() => {
      setSuccess('');
      setError('');
    }, 5000);
  };

  const resetForms = () => {
    setUserFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      phone: '',
      department: '',
      job_title: '',
      role_id: 4,
      is_active: true
    });
    setPasswordData({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    // FIXED: Initialize role form with complete permissions structure
    setRoleFormData({
      name: '',
      description: '',
      color: '#6b7280',
      permissions: createDefaultPermissions()
    });
    // FIXED: Initialize API key form with full permissions
    setApiKeyFormData({
      name: '',
      description: '',
      permissions: createFullPermissions(),
      allowed_ips: [],
      rate_limit: 1000,
      expires_days: 365
    });
    setEditingUser(null);
    setEditingRole(null);
    setEditingApiKey(null);
    setNewApiKey('');
  };

  // Enhanced form field update handlers
  const updateUserFormField = (field, value) => {
    setUserFormData(prevData => ({
      ...prevData,
      [field]: value
    }));
  };

  // ENHANCED: API functions with unified settings permission approach
  const fetchCompany = async () => {
    try {
      const response = await makeSettingsApiCall('/company/profile');
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setCompany(result.data);
        }
      }
    } catch (error) {
      console.error('Error fetching company:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await makeSettingsApiCall('/users');
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setUsers(result.data.users || result.data);
        }
      } else {
        console.error('Failed to fetch users');
        showMessage('Error fetching users', 'error');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      showMessage('Error fetching users', 'error');
    }
  };

  const fetchCurrentUser = async () => {
    try {
      // Current user endpoint should remain as-is (auth-specific)
      const response = await fetch(`${apiBaseUrl}/auth/current-user`, {
        credentials: 'include'
      });
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setCurrentUser(result.data);
        }
      }
    } catch (error) {
      console.error('Error fetching current user:', error);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await makeSettingsApiCall('/roles');
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setRoles(result.data);
        }
      } else {
        console.error('Failed to fetch roles');
        showMessage('Error fetching roles', 'error');
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
      showMessage('Error fetching roles', 'error');
    }
  };

  // ENHANCED: API key fetching with unified settings permission
  const fetchApiKeys = async () => {
    try {
      const response = await makeSettingsApiCall('/api-keys');
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setApiKeys(result.data);
        }
      } else {
        console.error('Failed to fetch API keys');
        showMessage('Error fetching API keys', 'error');
      }
    } catch (error) {
      console.error('Error fetching API keys:', error);
      showMessage('Error fetching API keys', 'error');
    }
  };

  // Load data on component mount and tab change
  useEffect(() => {
    if (activeTab === 'company') {
      fetchCompany();
    } else if (activeTab === 'users') {
      fetchUsers();
      fetchCurrentUser();
      fetchRoles();
    } else if (activeTab === 'roles') {
      fetchRoles();
    } else if (activeTab === 'api') {
      fetchApiKeys();
    }
  }, [activeTab]);

  // ENHANCED: Company handlers with unified settings permission
  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await makeSettingsApiCall('/company/profile', {
        method: 'PUT',
        body: company
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage('Company profile updated successfully');
          fetchCompany();
        } else {
          showMessage(result.error || 'Failed to update company profile', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to update company profile', 'error');
      }
    } catch (error) {
      console.error('Error updating company:', error);
      showMessage('Error updating company profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Profile handlers (keep auth-specific)
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(currentUser),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage(`Profile updated successfully! Updated: ${result.updated_fields?.join(', ') || 'profile'}`);
          setShowProfileDialog(false);
          fetchCurrentUser();
        } else {
          if (result.details && Array.isArray(result.details)) {
            showMessage(`Validation errors: ${result.details.join(', ')}`, 'error');
          } else {
            showMessage(result.error || 'Failed to update profile', 'error');
          }
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to update profile', 'error');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      showMessage('Error updating profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Enhanced edit user handler
  const handleEditUser = (user) => {
    try {
      setEditingUser(user);
      
      // Ensure all fields are properly set with fallbacks
      const formData = {
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        department: user.department || '',
        job_title: user.job_title || '',
        role_id: user.role_id || 4,
        is_active: user.is_active !== undefined ? user.is_active : true
      };
      
      setUserFormData(formData);
      setShowUserDialog(true);
    } catch (error) {
      console.error('Error setting up edit user:', error);
      showMessage('Error opening edit user dialog', 'error');
    }
  };

  // ENHANCED: User handlers with unified settings permission
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const method = editingUser ? 'PUT' : 'POST';
      const endpoint = editingUser ? `/users-edit/${editingUser.id}` : '/users';
      
      const response = await makeSettingsApiCall(endpoint, {
        method,
        body: userFormData
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage(`User ${editingUser ? 'updated' : 'created'} successfully`);
          setShowUserDialog(false);
          resetForms();
          fetchUsers();
        } else {
          showMessage(result.error || `Failed to ${editingUser ? 'update' : 'create'} user`, 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || `Failed to ${editingUser ? 'update' : 'create'} user`, 'error');
      }
    } catch (error) {
      console.error(`Error ${editingUser ? 'updating' : 'creating'} user:`, error);
      showMessage(`Error ${editingUser ? 'updating' : 'creating'} user`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // ENHANCED: Toggle user status with unified settings permission
  const handleToggleUserStatus = async (userId) => {
    try {
      setLoading(true);
      const response = await makeSettingsApiCall(`/users/${userId}/toggle-status`, {
        method: 'PUT'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage(result.message || 'User status updated successfully');
          fetchUsers(); // Refresh the user list
        } else {
          showMessage(result.error || 'Failed to toggle user status', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to toggle user status', 'error');
      }
    } catch (error) {
      console.error('Error toggling user status:', error);
      showMessage('Error toggling user status', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      showMessage('New passwords do not match', 'error');
      return;
    }

    if (passwordData.new_password.length < 8) {
      showMessage('New password must be at least 8 characters long', 'error');
      return;
    }

    setLoading(true);

    try {
      // Password change should remain auth-specific
      const response = await fetch(`${apiBaseUrl}/auth/password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage('Password changed successfully');
          setPasswordData({
            current_password: '',
            new_password: '',
            confirm_password: ''
          });
          setShowPasswordDialog(false);
        } else {
          showMessage(result.error || 'Failed to change password', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to change password', 'error');
      }
    } catch (error) {
      console.error('Error changing password:', error);
      showMessage('Error changing password', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ENHANCED: Role handlers with unified settings permission
  const handleRoleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Ensure permissions are properly structured before submission
      const submissionData = {
        ...roleFormData,
        permissions: ensureCompletePermissions(roleFormData.permissions)
      };

      const method = editingRole ? 'PUT' : 'POST';
      const endpoint = editingRole ? `/roles/${editingRole.id}` : '/roles';
      
      const response = await makeSettingsApiCall(endpoint, {
        method,
        body: submissionData
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage(`Role ${editingRole ? 'updated' : 'created'} successfully`);
          setShowRoleDialog(false);
          resetForms();
          fetchRoles();
        } else {
          showMessage(result.error || `Failed to ${editingRole ? 'update' : 'create'} role`, 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || `Failed to ${editingRole ? 'update' : 'create'} role`, 'error');
      }
    } catch (error) {
      console.error(`Error ${editingRole ? 'updating' : 'creating'} role:`, error);
      showMessage(`Error ${editingRole ? 'updating' : 'creating'} role`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRole = async (roleId) => {
    if (!confirm('Are you sure you want to delete this role?')) return;

    try {
      const response = await makeSettingsApiCall(`/roles/${roleId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage('Role deleted successfully');
          fetchRoles();
        } else {
          showMessage(result.error || 'Failed to delete role', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to delete role', 'error');
      }
    } catch (error) {
      console.error('Error deleting role:', error);
      showMessage('Error deleting role', 'error');
    }
  };

  // FIXED: Enhanced edit role handler
  const handleEditRole = (role) => {
    setEditingRole(role);
    
    // Ensure permissions are properly structured for editing
    const completePermissions = ensureCompletePermissions(role.permissions);
    
    setRoleFormData({
      name: role.name || '',
      description: role.description || '',
      color: role.color || '#6b7280',
      permissions: completePermissions
    });
    setShowRoleDialog(true);
  };

  // FIXED: Enhanced permission change handler
  const handlePermissionChange = (module, permission, value) => {
    setRoleFormData(prev => {
      // Ensure the module exists in permissions
      const currentPermissions = prev.permissions || {};
      const modulePermissions = currentPermissions[module] || {
        read: false,
        write: false,
        delete: false
      };

      return {
        ...prev,
        permissions: {
          ...currentPermissions,
          [module]: {
            ...modulePermissions,
            [permission]: value
          }
        }
      };
    });
  };

  // FIXED: Helper function to get permission value safely
  const getPermissionValue = (module, permission) => {
    return roleFormData.permissions?.[module]?.[permission] || false;
  };

  // FIXED: Enhanced API Key handlers with proper permission handling and key storage
  const handleApiKeySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const method = editingApiKey ? 'PUT' : 'POST';
      const endpoint = editingApiKey ? `/api-keys/${editingApiKey.id}` : '/api-keys';
      
      // FIXED: Ensure new API keys have full permissions and log what we're sending
      const fullPermissions = createFullPermissions();
      console.log('Sending permissions:', fullPermissions); // Debug log
      
      const submissionData = {
        ...apiKeyFormData,
        permissions: editingApiKey ? apiKeyFormData.permissions : fullPermissions
      };
      
      console.log('Full submission data:', submissionData); // Debug log
      
      const response = await makeSettingsApiCall(endpoint, {
        method,
        body: submissionData
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          if (!editingApiKey && result.data.api_key) {
            // FIXED: Store the full API key for copy/display functionality
            setNewApiKey(result.data.api_key);
            setFullKeys(prev => new Map(prev).set(result.data.id, result.data.api_key));
            
            // Update the API keys list with the new key
            setApiKeys(prev => [result.data, ...prev]);
          }
          showMessage(`API Key ${editingApiKey ? 'updated' : 'created'} successfully`);
          setShowApiKeyDialog(false);
          resetForms();
          if (editingApiKey) {
            fetchApiKeys(); // Only refetch if editing
          }
        } else {
          showMessage(result.error || `Failed to ${editingApiKey ? 'update' : 'create'} API key`, 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || `Failed to ${editingApiKey ? 'update' : 'create'} API key`, 'error');
      }
    } catch (error) {
      console.error(`Error ${editingApiKey ? 'updating' : 'creating'} API key:`, error);
      showMessage(`Error ${editingApiKey ? 'updating' : 'creating'} API key`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteApiKey = async (apiKeyId) => {
    if (!confirm('Are you sure you want to delete this API key?')) return;

    try {
      const response = await makeSettingsApiCall(`/api-keys/${apiKeyId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          showMessage('API key deleted successfully');
          // Remove from full keys map
          setFullKeys(prev => {
            const newMap = new Map(prev);
            newMap.delete(apiKeyId);
            return newMap;
          });
          fetchApiKeys();
        } else {
          showMessage(result.error || 'Failed to delete API key', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to delete API key', 'error');
      }
    } catch (error) {
      console.error('Error deleting API key:', error);
      showMessage('Error deleting API key', 'error');
    }
  };

  // FIXED: Enhanced regenerate API key handler
  const handleRegenerateApiKey = async (apiKeyId) => {
    if (!confirm('Are you sure you want to regenerate this API key? The old key will stop working immediately.')) return;

    try {
      setLoading(true);
      const response = await makeSettingsApiCall(`/api-keys/${apiKeyId}/regenerate`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data.api_key) {
          // FIXED: Store the new full key for copy/display functionality
          setFullKeys(prev => new Map(prev).set(apiKeyId, result.data.api_key));
          setNewApiKey(result.data.api_key);
          
          // Update the specific API key in the list
          setApiKeys(prev => prev.map(key => 
            key.id === apiKeyId ? result.data : key
          ));
          
          showMessage('API key regenerated successfully');
        } else {
          showMessage(result.error || 'Failed to regenerate API key', 'error');
        }
      } else {
        const errorData = await response.json();
        showMessage(errorData.error || 'Failed to regenerate API key', 'error');
      }
    } catch (error) {
      console.error('Error regenerating API key:', error);
      showMessage('Error regenerating API key', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account, company, and system settings</p>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center">
          <CheckCircle className="h-5 w-5 mr-2" />
          {success}
        </div>
      )}

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'company', name: 'Company', icon: Building2 },
              { id: 'users', name: 'Users', icon: Users },
              { id: 'roles', name: 'Roles', icon: Shield },
              { id: 'api', name: 'API Keys', icon: Key }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-emerald-500 text-emerald-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Company Tab */}
          {activeTab === 'company' && (
            <div className="max-w-4xl">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Company Information</h2>
                <p className="text-gray-600">Update your company profile and settings</p>
              </div>

              <form onSubmit={handleCompanySubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name
                    </label>
                    <input
                      type="text"
                      value={company.name}
                      onChange={(e) => setCompany({...company, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Legal Name
                    </label>
                    <input
                      type="text"
                      value={company.legal_name}
                      onChange={(e) => setCompany({...company, legal_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Industry
                    </label>
                    <input
                      type="text"
                      value={company.industry}
                      onChange={(e) => setCompany({...company, industry: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Website
                    </label>
                    <input
                      type="url"
                      value={company.website}
                      onChange={(e) => setCompany({...company, website: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={company.description}
                    onChange={(e) => setCompany({...company, description: e.target.value})}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Save className="h-4 w-4" />
                    <span>{loading ? 'Saving...' : 'Save Changes'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div className="max-w-6xl">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">User Management</h2>
                  <p className="text-gray-600">Manage user accounts and permissions</p>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowProfileDialog(true)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
                  >
                    <User className="h-4 w-4" />
                    <span>Edit Profile</span>
                  </button>
                  <button
                    onClick={() => setShowPasswordDialog(true)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
                  >
                    <Key className="h-4 w-4" />
                    <span>Change Password</span>
                  </button>
                  <button
                    onClick={() => {
                      resetForms();
                      setShowUserDialog(true);
                    }}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center space-x-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add User</span>
                  </button>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Role
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Last Login
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-10 w-10">
                                <div className="h-10 w-10 rounded-full bg-emerald-500 flex items-center justify-center">
                                  <span className="text-sm font-medium text-white">
                                    {user.first_name?.[0]}{user.last_name?.[0]}
                                  </span>
                                </div>
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">
                                  {user.first_name} {user.last_name}
                                </div>
                                <div className="text-sm text-gray-500">{user.email}</div>
                                <div className="text-xs text-gray-400">@{user.username}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span 
                              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                              style={{ 
                                backgroundColor: `${user.role_color || '#6b7280'}20`, 
                                color: user.role_color || '#6b7280'
                              }}
                            >
                              {user.role_name || 'Unknown'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              user.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => handleEditUser(user)}
                                className="text-emerald-600 hover:text-emerald-700 p-1 rounded"
                                title="Edit User"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleToggleUserStatus(user.id)}
                                className={`p-1 rounded ${
                                  user.is_active 
                                    ? 'text-red-600 hover:text-red-700' 
                                    : 'text-green-600 hover:text-green-700'
                                }`}
                                title={user.is_active ? 'Disable Account' : 'Enable Account'}
                                disabled={loading}
                              >
                                {user.is_active ? <XCircle className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* FIXED: Enhanced Roles Tab with all permission modules */}
          {activeTab === 'roles' && (
            <div className="max-w-6xl">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Role Management</h2>
                  <p className="text-gray-600">Configure roles and permissions</p>
                </div>
                <button
                  onClick={() => {
                    resetForms();
                    // Initialize with complete permissions structure
                    setRoleFormData({
                      name: '',
                      description: '',
                      color: '#6b7280',
                      permissions: createDefaultPermissions()
                    });
                    setShowRoleDialog(true);
                  }}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Role</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {roles.map((role) => (
                  <div key={role.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: role.color }}
                        />
                        <h3 className="text-lg font-semibold text-gray-900">{role.name}</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEditRole(role)}
                          className="text-emerald-600 hover:text-emerald-700 p-1 rounded"
                          title="Edit Role"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        {!role.is_system_role && (
                          <button
                            onClick={() => handleDeleteRole(role.id)}
                            className="text-red-600 hover:text-red-700 p-1 rounded"
                            title="Delete Role"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-4">{role.description}</p>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">
                        {role.user_count || 0} users
                      </span>
                      {role.is_system_role && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                          System Role
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* FIXED: Enhanced API Keys Tab with proper key management */}
          {activeTab === 'api' && (
            <div className="max-w-6xl">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">API Key Management</h2>
                  <p className="text-gray-600">Manage API keys for external integrations</p>
                </div>
                <button
                  onClick={() => {
                    resetForms();
                    setShowApiKeyDialog(true);
                  }}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Generate API Key</span>
                </button>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Name & Description
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          API Key
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Last Used
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {apiKeys.map((apiKey) => (
                        <tr key={apiKey.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{apiKey.name}</div>
                              <div className="text-sm text-gray-500">{apiKey.description || 'No description'}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-2">
                              <div className="flex-1 min-w-0">
                                <code className="text-sm font-mono text-gray-800 bg-gray-50 px-2 py-1 rounded border break-all">
                                  {formatApiKey(
                                    apiKey.id,
                                    apiKey.key_prefix,
                                    visibleKeys.has(apiKey.id)
                                  )}
                                </code>
                              </div>
                              <div className="flex items-center space-x-1">
                                {/* FIXED: Toggle visibility button */}
                                <button
                                  onClick={() => toggleKeyVisibility(apiKey.id)}
                                  className="p-1 text-gray-500 hover:text-gray-700 rounded"
                                  title={visibleKeys.has(apiKey.id) ? 'Hide API key' : 'Show API key'}
                                  disabled={!fullKeys.has(apiKey.id)}
                                >
                                  {visibleKeys.has(apiKey.id) ? (
                                    <EyeOff className="h-4 w-4" />
                                  ) : (
                                    <Eye className="h-4 w-4" />
                                  )}
                                </button>
                                {/* FIXED: Copy button with proper functionality */}
                                <button
                                  onClick={() => copyApiKey(apiKey.id)}
                                  className="p-1 text-gray-500 hover:text-gray-700 rounded"
                                  title="Copy API key"
                                  disabled={!fullKeys.has(apiKey.id)}
                                >
                                  {copiedKeys.has(apiKey.id) ? (
                                    <Check className="h-4 w-4 text-green-600" />
                                  ) : (
                                    <Copy className="h-4 w-4" />
                                  )}
                                </button>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              apiKey.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {apiKey.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {apiKey.last_used ? new Date(apiKey.last_used).toLocaleDateString() : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => {
                                  setEditingApiKey(apiKey);
                                  setApiKeyFormData({
                                    name: apiKey.name,
                                    description: apiKey.description,
                                    permissions: apiKey.permissions || createFullPermissions(),
                                    allowed_ips: apiKey.allowed_ips || [],
                                    rate_limit: apiKey.rate_limit || 1000,
                                    expires_days: 365
                                  });
                                  setShowApiKeyDialog(true);
                                }}
                                className="text-emerald-600 hover:text-emerald-700 p-1 rounded"
                                title="Edit API Key"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleRegenerateApiKey(apiKey.id)}
                                className="text-blue-600 hover:text-blue-700 p-1 rounded"
                                title="Regenerate API Key"
                                disabled={loading}
                              >
                                <RefreshCw className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteApiKey(apiKey.id)}
                                className="text-red-600 hover:text-red-700 p-1 rounded"
                                title="Delete API Key"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* User Dialog */}
      {showUserDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingUser ? 'Edit User' : 'Add New User'}
              </h3>
            </div>
            <form onSubmit={handleUserSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    value={userFormData.username}
                    onChange={(e) => updateUserFormField('username', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={userFormData.email}
                    onChange={(e) => updateUserFormField('email', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={userFormData.first_name}
                    onChange={(e) => updateUserFormField('first_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={userFormData.last_name}
                    onChange={(e) => updateUserFormField('last_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={userFormData.phone}
                    onChange={(e) => updateUserFormField('phone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={userFormData.department}
                    onChange={(e) => updateUserFormField('department', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Job Title
                  </label>
                  <input
                    type="text"
                    value={userFormData.job_title}
                    onChange={(e) => updateUserFormField('job_title', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={userFormData.role_id}
                    onChange={(e) => updateUserFormField('role_id', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  >
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={userFormData.is_active}
                  onChange={(e) => updateUserFormField('is_active', e.target.checked)}
                  className="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  Active Account
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowUserDialog(false);
                    resetForms();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Save className="h-4 w-4" />
                  <span>{loading ? 'Saving...' : (editingUser ? 'Update User' : 'Create User')}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Password Dialog */}
      {showPasswordDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Change Password</h3>
            </div>
            <form onSubmit={handlePasswordSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  required
                  minLength="8"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  required
                  minLength="8"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordDialog(false);
                    setPasswordData({
                      current_password: '',
                      new_password: '',
                      confirm_password: ''
                    });
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Key className="h-4 w-4" />
                  <span>{loading ? 'Changing...' : 'Change Password'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Profile Dialog */}
      {showProfileDialog && currentUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Edit Profile</h3>
            </div>
            <form onSubmit={handleProfileSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={currentUser.first_name || ''}
                    onChange={(e) => setCurrentUser({...currentUser, first_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={currentUser.last_name || ''}
                    onChange={(e) => setCurrentUser({...currentUser, last_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={currentUser.email || ''}
                    onChange={(e) => setCurrentUser({...currentUser, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={currentUser.phone || ''}
                    onChange={(e) => setCurrentUser({...currentUser, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={currentUser.department || ''}
                    onChange={(e) => setCurrentUser({...currentUser, department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Job Title
                  </label>
                  <input
                    type="text"
                    value={currentUser.job_title || ''}
                    onChange={(e) => setCurrentUser({...currentUser, job_title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileDialog(false);
                    fetchCurrentUser(); // Reset to original data
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Save className="h-4 w-4" />
                  <span>{loading ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* FIXED: Enhanced Role Dialog with all permission modules */}
      {showRoleDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingRole ? 'Edit Role' : 'Create New Role'}
              </h3>
            </div>
            <form onSubmit={handleRoleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role Name
                  </label>
                  <input
                    type="text"
                    value={roleFormData.name}
                    onChange={(e) => setRoleFormData({...roleFormData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Color
                  </label>
                  <input
                    type="color"
                    value={roleFormData.color}
                    onChange={(e) => setRoleFormData({...roleFormData, color: e.target.value})}
                    className="w-full h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={roleFormData.description}
                  onChange={(e) => setRoleFormData({...roleFormData, description: e.target.value})}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Permissions
                </label>
                <div className="space-y-4">
                  {permissionModules.map((module) => (
                    <div key={module} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3 capitalize">
                        {module.replace('_', ' ')}
                      </h4>
                      <div className="grid grid-cols-3 gap-4">
                        {['read', 'write', 'delete'].map((permission) => (
                          <label key={permission} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={getPermissionValue(module, permission)}
                              onChange={(e) => handlePermissionChange(module, permission, e.target.checked)}
                              className="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-sm text-gray-700 capitalize">
                              {permission}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowRoleDialog(false);
                    resetForms();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Save className="h-4 w-4" />
                  <span>{loading ? 'Saving...' : (editingRole ? 'Update Role' : 'Create Role')}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* API Key Dialog */}
      {showApiKeyDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingApiKey ? 'Edit API Key' : 'Generate New API Key'}
              </h3>
            </div>
            <form onSubmit={handleApiKeySubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={apiKeyFormData.name}
                    onChange={(e) => setApiKeyFormData({...apiKeyFormData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rate Limit (requests/hour)
                  </label>
                  <input
                    type="number"
                    value={apiKeyFormData.rate_limit}
                    onChange={(e) => setApiKeyFormData({...apiKeyFormData, rate_limit: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    min="1"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={apiKeyFormData.description}
                  onChange={(e) => setApiKeyFormData({...apiKeyFormData, description: e.target.value})}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowApiKeyDialog(false);
                    resetForms();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Key className="h-4 w-4" />
                  <span>{loading ? 'Generating...' : (editingApiKey ? 'Update API Key' : 'Generate API Key')}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* FIXED: Enhanced New API Key Display with working copy button */}
      {newApiKey && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">API Key Generated</h3>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-600 mb-4">
                Your new API key has been generated with full permissions. Please copy it now as you won't be able to see it again.
              </p>
              <div className="bg-gray-50 p-3 rounded-lg border">
                <div className="flex items-center justify-between">
                  <code className="text-sm font-mono text-gray-800 break-all">
                    {newApiKey}
                  </code>
                  <button
                    onClick={copyNewApiKey}
                    className="ml-2 p-1 text-gray-500 hover:text-gray-700"
                    title="Copy to clipboard"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="flex justify-end mt-4">
                <button
                  onClick={() => setNewApiKey('')}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

