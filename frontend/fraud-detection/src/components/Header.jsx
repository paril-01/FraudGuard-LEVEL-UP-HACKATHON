import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import {
  TextField,
  InputAdornment,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
  Typography,
  Button
} from '@mui/material';
import { useNotifications } from '../context/NotificationContext';

const Header = ({ toggleSidebar }) => {
  const navigate = useNavigate();
  const [anchorElNotifications, setAnchorElNotifications] = useState(null);
  const [anchorElUser, setAnchorElUser] = useState(null);
  
  // Use the notifications context safely
  const notificationContext = useNotifications() || { 
    notifications: [], 
    markAsRead: () => {}, 
    clearNotifications: () => {},
    unreadCount: 0
  };
  
  const { 
    notifications = [], 
    markAsRead = () => {}, 
    removeNotification = () => {},
    clearNotifications = () => {}
  } = notificationContext;

  // Get unread count safely
  const getUnreadCount = () => {
    return notifications.filter(n => !n.read).length;
  };
  
  // Handle marking all as read
  const markAllAsRead = () => {
    if (notifications.length > 0) {
      notifications.forEach(notification => {
        if (!notification.read) {
          markAsRead(notification.id);
        }
      });
    }
  };
  
  // Get user data from localStorage
  const getUserData = () => {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : { name: 'User', email: 'user@example.com' };
  };
  
  const user = getUserData();

  const handleNotificationsMenuClick = (event) => {
    setAnchorElNotifications(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setAnchorElNotifications(null);
  };

  const handleUserMenuClick = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorElUser(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    navigate('/login');
  };
  
  const handleSettings = () => {
    handleUserMenuClose();
    navigate('/settings');
  };
  
  const handleMarkAllRead = () => {
    markAllAsRead();
  };
  
  const handleNotificationClick = (id) => {
    markAsRead(id);
    // Find notification to determine where to navigate
    const notification = notifications.find(n => n.id === id);
    if (notification?.link) {
      navigate(notification.link);
    }
    handleNotificationClose();
  };

  // Format the notification timestamp
  const formatNotificationTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHr / 24);
    
    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <header className="app-header">
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={toggleSidebar}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <TextField
          placeholder="Search..."
          variant="outlined"
          size="small"
          sx={{ 
            backgroundColor: 'var(--gray-100)', 
            borderRadius: '20px', 
            '& .MuiOutlinedInput-root': { 
              borderRadius: '20px', 
              height: '40px'
            } 
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <IconButton color="inherit" onClick={handleNotificationsMenuClick}>
          <Badge badgeContent={getUnreadCount()} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <Menu
          anchorEl={anchorElNotifications}
          open={Boolean(anchorElNotifications)}
          onClose={handleNotificationClose}
          PaperProps={{
            sx: { width: 320, maxHeight: 400 }
          }}
        >
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Notifications</Typography>
            {getUnreadCount() > 0 && (
              <Button 
                color="primary" 
                size="small" 
                onClick={handleMarkAllRead}
              >
                Mark all as read
              </Button>
            )}
          </Box>
          <Divider />
          
          {notifications.length === 0 ? (
            <MenuItem onClick={handleNotificationClose}>No notifications</MenuItem>
          ) : (
            notifications.map((notification) => (
              <MenuItem 
                key={notification.id} 
                onClick={() => handleNotificationClick(notification.id)}
                sx={{ 
                  whiteSpace: 'normal',
                  backgroundColor: notification.read ? 'inherit' : 'rgba(25, 118, 210, 0.08)',
                  py: 1
                }}
              >
                <Box sx={{ width: '100%' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography 
                      variant="subtitle2" 
                      color={notification.type === 'error' ? 'error.main' : 
                             notification.type === 'success' ? 'success.main' : 'text.primary'}
                      fontWeight={notification.read ? 'normal' : 'bold'}
                    >
                      {notification.title || (notification.type === 'error' ? 'Alert' : 
                                             notification.type === 'success' ? 'Success' : 'Notification')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatNotificationTime(notification.timestamp)}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {notification.message}
                  </Typography>
                </Box>
              </MenuItem>
            ))
          )}
        </Menu>

        <IconButton onClick={handleUserMenuClick} sx={{ p: 0, ml: 2 }}>
          <Avatar sx={{ bgcolor: 'var(--primary-color)', width: 40, height: 40 }}>
            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
          </Avatar>
        </IconButton>
        <Menu
          anchorEl={anchorElUser}
          open={Boolean(anchorElUser)}
          onClose={handleUserMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem disabled>
            <ListItemText primary={user?.name || 'User'} secondary={user?.email || 'user@example.com'} />
          </MenuItem>
          <MenuItem onClick={handleSettings}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            Settings
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            Logout
          </MenuItem>
        </Menu>
      </Box>
    </header>
  );
};

export default Header; 