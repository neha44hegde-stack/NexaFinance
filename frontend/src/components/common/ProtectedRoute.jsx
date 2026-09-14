import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className=\"min-h-screen flex items-center justify-center\">
        <div className=\"animate-spin rounded-full h-12 w-12 border-4 border-primary-green border-t-transparent\"></div>
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to=\"/login\" />;
};

export default ProtectedRoute;
