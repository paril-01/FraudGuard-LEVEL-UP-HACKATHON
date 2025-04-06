import { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

// Create the auth context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Check for existing session on initial load
  useEffect(() => {
    const checkAuth = () => {
      const auth = localStorage.getItem('isAuthenticated') === 'true';
      const userData = localStorage.getItem('user');
      
      if (auth && userData) {
        setIsAuthenticated(true);
        setUser(JSON.parse(userData));
      } else {
        // If not authenticated and not on login page, redirect to login
        if (location.pathname !== '/login') {
          navigate('/login');
        }
      }
      
      setLoading(false);
    };

    checkAuth();
  }, [navigate, location.pathname]);

  // Login function
  const login = (userData) => {
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
    navigate('/');
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
    navigate('/login');
  };

  // Authentication check function
  const requireAuth = (Component) => {
    if (!isAuthenticated && !loading) {
      navigate('/login');
      return null;
    }
    return Component;
  };

  const contextValue = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    requireAuth
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected route wrapper component
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!loading && !isAuthenticated && location.pathname !== '/login') {
      navigate('/login');
    }
  }, [isAuthenticated, loading, navigate, location]);

  if (loading) {
    return <div className="loading-container">Authenticating...</div>;
  }

  return isAuthenticated ? children : null;
};

export default AuthContext; 