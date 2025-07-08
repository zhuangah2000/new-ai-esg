import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { Eye, EyeOff, Leaf, AlertCircle, UserCheck, ArrowLeft } from 'lucide-react';

export const Login = ({ apiBaseUrl }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showResetModal, setShowResetModal] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);

  const { login, isAuthenticated, sessionReady, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get the intended destination or default to dashboard
  const from = location.state?.from?.pathname || '/dashboard';

  // Redirect if already authenticated and session is ready
  useEffect(() => {
    if (isAuthenticated && sessionReady && user) {
      console.log('✅ User authenticated and session ready, redirecting to:', from);
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, sessionReady, user, navigate, from]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError('');
    setLoginSuccess(false);

    try {
      console.log('🔐 Submitting login form...');
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        console.log('✅ Login successful, waiting for session establishment...');
        setLoginSuccess(true);
        // Don't redirect here - let the useEffect handle it when sessionReady becomes true
      } else {
        console.log('❌ Login failed:', result.error);
        setError(result.error || 'Invalid credentials. Please try again.');
      }
    } catch (error) {
      console.error('❌ Login submission error:', error);
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const openResetModal = () => {
    setShowResetModal(true);
  };

  const closeResetModal = () => {
    setShowResetModal(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Main Login Card */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-8 py-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-4">
              <Leaf className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">CarbonView</h1>
            <p className="text-green-100 text-sm">ESG Reporting Platform</p>
          </div>

          {/* Form Section */}
          <div className="px-8 py-8">
            {loginSuccess ? (
              /* Success State - Show while waiting for session */
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Login Successful!</h2>
                <p className="text-gray-600 text-sm">Setting up your session...</p>
              </div>
            ) : (
              /* Login Form */
              <>
                <div className="text-center mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Welcome Back</h2>
                  <p className="text-gray-600 text-sm">Sign in to continue to your dashboard</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Username Field */}
                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                      Username
                    </label>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      value={formData.username}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors text-gray-900 placeholder-gray-500"
                      placeholder="Enter your username"
                      disabled={loading}
                    />
                  </div>

                  {/* Password Field */}
                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        required
                        value={formData.password}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors text-gray-900 placeholder-gray-500"
                        placeholder="Enter your password"
                        disabled={loading}
                      />
                      <button
                        type="button"
                        onClick={togglePasswordVisibility}
                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                        disabled={loading}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Forgot Password Link */}
                  <div className="text-right">
                    <button
                      type="button"
                      onClick={openResetModal}
                      className="text-sm text-green-600 hover:text-green-700 hover:underline transition-colors"
                      disabled={loading}
                    >
                      Forgot your password?
                    </button>
                  </div>

                  {/* Error Message */}
                  {error && (
                    <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                      <span className="text-sm text-red-700">{error}</span>
                    </div>
                  )}

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Signing in...
                      </div>
                    ) : (
                      'Sign In'
                    )}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-500">
            © 2025 CarbonView. All rights reserved.
          </p>
        </div>
      </div>

      {/* Password Reset Modal - Simplified Admin Contact */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4 text-center">
              <h3 className="text-lg font-semibold text-white">Password Reset</h3>
            </div>

            {/* Modal Content - Admin Contact Message */}
            <div className="p-8 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
                <UserCheck className="w-8 h-8 text-green-600" />
              </div>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                Need to Reset Your Password?
              </h4>
              
              <p className="text-gray-600 mb-6 leading-relaxed">
                Please contact your <strong>Platform Administrator</strong> for password reset assistance.
              </p>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-green-800">
                  <strong>Note:</strong> Password resets are handled securely by your system administrator to ensure account security.
                </p>
              </div>

              {/* Close Button */}
              <button
                type="button"
                onClick={closeResetModal}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <ArrowLeft className="h-4 w-4 inline mr-2" />
                Back to Login
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

