import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  BarChart3,
  Zap,
  Activity,
  Users,
  FileText,
  Settings,
  Menu,
  Leaf,
  FolderOpen,
  HardDrive,
  Target,
  LogOut,
  User,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from './AuthContext';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Emission Factors', href: '/emission-factors', icon: Zap },
  { name: 'Measurements', href: '/measurements', icon: Activity },
  { name: 'Suppliers', href: '/suppliers', icon: Users },
  { name: 'Projects', href: '/projects', icon: FolderOpen },
  { name: 'Assets', href: '/assets', icon: HardDrive },
  { name: 'ESG Targets', href: '/esg-targets', icon: Target },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar({ isOpen, onToggle }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  // Get user display information
  const getUserDisplayName = () => {
    if (!user) return 'Loading...';
    
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    } else if (user.first_name) {
      return user.first_name;
    } else {
      return user.username;
    }
  };

  const getUserRole = () => {
    if (!user) return '';
    return user.role_name || 'User';
  };

  const getUserEmail = () => {
    if (!user) return '';
    return user.email || '';
  };

  const getUserInitials = () => {
    if (!user) return '?';
    
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    } else if (user.first_name) {
      return user.first_name[0].toUpperCase();
    } else {
      return user.username[0].toUpperCase();
    }
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setLoggingOut(false);
    }
  };

  const toggleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
  };

  return (
    <div className={`fixed inset-y-0 left-0 z-50 bg-white shadow-lg transition-all duration-300 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-600">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            {isOpen && (
              <span className="text-xl font-bold text-gray-900">CarbonView</span>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="h-8 w-8 p-0"
          >
            <Menu className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-green-100 text-green-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon
                  className={`mr-3 h-5 w-5 flex-shrink-0 ${
                    isActive ? 'text-green-600' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                {isOpen && item.name}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="border-t">
          {isOpen ? (
            /* Expanded User Profile */
            <div className="p-4">
              <div 
                className="flex items-center justify-between cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors"
                onClick={toggleUserMenu}
              >
                <div className="flex items-center min-w-0 flex-1">
                  {/* User Avatar */}
                  <div className="h-8 w-8 rounded-full bg-green-600 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                    {getUserInitials()}
                  </div>
                  
                  {/* User Info */}
                  <div className="ml-3 min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-700 truncate">
                      {getUserDisplayName()}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {getUserRole()}
                    </p>
                  </div>
                </div>
                
                {/* Dropdown Arrow */}
                <div className="ml-2 flex-shrink-0">
                  {userMenuOpen ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </div>

              {/* User Menu Dropdown */}
              {userMenuOpen && (
                <div className="mt-2 space-y-1">
                  {/* User Email */}
                  <div className="px-2 py-1">
                    <p className="text-xs text-gray-500 truncate">
                      {getUserEmail()}
                    </p>
                  </div>
                  
                  {/* Profile Link */}
                  <Link
                    to="/settings"
                    className="flex items-center px-2 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md transition-colors"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User className="h-4 w-4 mr-2 text-gray-400" />
                    Profile Settings
                  </Link>
                  
                  {/* Logout Button */}
                  <button
                    onClick={handleLogout}
                    disabled={loggingOut}
                    className="w-full flex items-center px-2 py-2 text-sm text-red-600 hover:bg-red-50 hover:text-red-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    {loggingOut ? 'Signing out...' : 'Sign Out'}
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* Collapsed User Profile */
            <div className="p-2">
              <div className="relative group">
                {/* User Avatar */}
                <div className="h-8 w-8 rounded-full bg-green-600 flex items-center justify-center text-white text-sm font-medium mx-auto cursor-pointer">
                  {getUserInitials()}
                </div>
                
                {/* Tooltip on Hover */}
                <div className="absolute left-full ml-2 top-0 bg-gray-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                  {getUserDisplayName()}
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 border-4 border-transparent border-r-gray-900"></div>
                </div>
              </div>
              
              {/* Logout Button for Collapsed State */}
              <button
                onClick={handleLogout}
                disabled={loggingOut}
                className="w-full mt-2 p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed group"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4 mx-auto" />
                
                {/* Tooltip */}
                <div className="absolute left-full ml-2 top-0 bg-gray-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                  Sign Out
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 border-4 border-transparent border-r-gray-900"></div>
                </div>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

