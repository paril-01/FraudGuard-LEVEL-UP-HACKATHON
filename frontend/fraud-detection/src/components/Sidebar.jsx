import { Link, useLocation } from 'react-router-dom';
import { 
  Dashboard as DashboardIcon,
  AccountBalanceWallet as BlockchainIcon,
  BarChart as AnalysisIcon,
  People as UserIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  SwapHoriz as TransactionIcon
} from '@mui/icons-material';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  
  // Navigation items
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { path: '/blockchain', label: 'Blockchain Hub', icon: <BlockchainIcon /> },
    { path: '/analysis', label: 'Transaction Analysis', icon: <AnalysisIcon /> },
    { path: '/transactions', label: 'Transactions', icon: <TransactionIcon /> },
    { path: '/users', label: 'User Management', icon: <UserIcon /> },
    { path: '/settings', label: 'Settings', icon: <SettingsIcon /> },
  ];

  return (
    <div className={`sidebar ${!isOpen ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h2>Analytics Hub</h2>
        {isOpen && (
          <button className="close-sidebar" onClick={onClose}>
            <CloseIcon />
          </button>
        )}
      </div>
      
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link 
                to={item.path} 
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar; 