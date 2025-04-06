import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = ({ children, title }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [navigate]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="app-container">
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
      
      <div className="main-content" style={{ 
        marginLeft: isSidebarOpen ? 'var(--sidebar-width)' : '0',
        transition: 'margin 0.3s ease'
      }}>
        <Header toggleSidebar={toggleSidebar} title={title} />
        <div className="content-wrapper">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout; 