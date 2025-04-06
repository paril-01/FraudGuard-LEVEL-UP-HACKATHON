import { createContext, useContext, useState } from 'react';

// Create notification context
const NotificationContext = createContext();

// Custom hook to use the notification context
export const useNotifications = () => {
  return useContext(NotificationContext);
};

// Provider component to wrap around the app
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  // Add a new notification
  const addNotification = (notification) => {
    setNotifications((prev) => [
      {
        id: Date.now(), // Unique ID
        read: false,
        ...notification,
      },
      ...prev,
    ]);
  };

  // Mark a notification as read
  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === id
          ? { ...notification, read: true }
          : notification
      )
    );
  };

  // Remove a notification
  const removeNotification = (id) => {
    setNotifications((prev) =>
      prev.filter((notification) => notification.id !== id)
    );
  };

  // Clear all notifications
  const clearNotifications = () => {
    setNotifications([]);
  };

  // Count unread notifications
  const unreadCount = notifications.filter(
    (notification) => !notification.read
  ).length;

  // Value object to be provided to context consumers
  const value = {
    notifications,
    addNotification,
    markAsRead,
    removeNotification,
    clearNotifications,
    unreadCount,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext; 