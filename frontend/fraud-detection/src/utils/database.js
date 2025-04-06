/**
 * SQLite Database Utility for FraudGuard
 * 
 * This module provides a client-side SQLite database implementation
 * for storing user accounts and transaction history in the browser.
 * Note: In a production environment, this would be implemented on the server.
 */

import { openDB } from 'idb';

// Database initialization promise to ensure it's ready before use
let dbPromise = null;

// Initialize the IndexedDB database (simulating SQLite)
const initDB = async () => {
  if (!dbPromise) {
    dbPromise = openDB('fraudguard-db', 1, {
      upgrade(db) {
        // Create users table
        if (!db.objectStoreNames.contains('users')) {
          const userStore = db.createObjectStore('users', { keyPath: 'email' });
          userStore.createIndex('email', 'email', { unique: true });
        }
        
        // Create transactions table
        if (!db.objectStoreNames.contains('transactions')) {
          const txStore = db.createObjectStore('transactions', { keyPath: 'id', autoIncrement: true });
          txStore.createIndex('userId', 'userId', { unique: false });
          txStore.createIndex('timestamp', 'timestamp', { unique: false });
          txStore.createIndex('hash', 'hash', { unique: false });
        }
        
        // Create wallet connections table
        if (!db.objectStoreNames.contains('wallets')) {
          const walletStore = db.createObjectStore('wallets', { keyPath: 'id', autoIncrement: true });
          walletStore.createIndex('userId', 'userId', { unique: false });
          walletStore.createIndex('address', 'address', { unique: true });
        }
        
        // Create login attempts table for security monitoring
        if (!db.objectStoreNames.contains('loginAttempts')) {
          const attemptsStore = db.createObjectStore('loginAttempts', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          attemptsStore.createIndex('email', 'email', { unique: false });
          attemptsStore.createIndex('timestamp', 'timestamp', { unique: false });
          attemptsStore.createIndex('ip', 'ip', { unique: false });
        }
      }
    });
  }
  
  return dbPromise;
};

// Initialize the database as soon as this module is imported
initDB().catch(err => console.error('Database initialization failed:', err));

// User related operations
export const userDB = {
  async createUser({ email, password, name, role = 'User' }) {
    try {
      const db = await initDB();
      const hashedPassword = await hashPassword(password);
      
      // Create user with hashed password
      await db.put('users', {
        email,
        password: hashedPassword,
        name,
        role,
        createdAt: new Date().toISOString(),
        lastLogin: null
      });
      
      return { email, name, role };
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  },
  
  async getUserByEmail(email) {
    try {
      const db = await initDB();
      return db.get('users', email);
    } catch (error) {
      console.error('Error getting user by email:', error);
      throw error;
    }
  },
  
  async verifyUser(email, password) {
    try {
      const user = await this.getUserByEmail(email);
      if (!user) return null;
      
      const passwordMatches = await verifyPassword(password, user.password);
      if (!passwordMatches) return null;
      
      // Update last login timestamp
      const db = await initDB();
      await db.put('users', {
        ...user,
        lastLogin: new Date().toISOString()
      });
      
      // Return user data without password
      const { password: _, ...userData } = user;
      return userData;
    } catch (error) {
      console.error('Error verifying user:', error);
      throw error;
    }
  },
  
  async updateUserProfile(email, updates) {
    try {
      const db = await initDB();
      const user = await this.getUserByEmail(email);
      if (!user) throw new Error('User not found');
      
      await db.put('users', {
        ...user,
        ...updates,
        updatedAt: new Date().toISOString()
      });
      
      return { success: true };
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  }
};

// Transaction related operations
export const transactionDB = {
  async addTransaction(transaction) {
    try {
      const db = await initDB();
      return db.add('transactions', {
        ...transaction,
        timestamp: transaction.timestamp || new Date().toISOString()
      });
    } catch (error) {
      console.error('Error adding transaction:', error);
      throw error;
    }
  },
  
  async getTransactionsByUser(userId) {
    try {
      const db = await initDB();
      const tx = db.transaction('transactions', 'readonly');
      const index = tx.store.index('userId');
      return index.getAll(userId);
    } catch (error) {
      console.error('Error getting transactions by user:', error);
      throw error;
    }
  },
  
  async getTransactionByHash(hash) {
    try {
      const db = await initDB();
      const tx = db.transaction('transactions', 'readonly');
      const index = tx.store.index('hash');
      return index.get(hash);
    } catch (error) {
      console.error('Error getting transaction by hash:', error);
      throw error;
    }
  },
  
  async updateTransaction(id, updates) {
    try {
      const db = await initDB();
      const transaction = await db.get('transactions', id);
      if (!transaction) throw new Error('Transaction not found');
      
      return db.put('transactions', {
        ...transaction,
        ...updates,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating transaction:', error);
      throw error;
    }
  }
};

// Wallet related operations
export const walletDB = {
  async connectWallet(userId, address, provider = 'metamask') {
    try {
      const db = await initDB();
      return db.add('wallets', {
        userId,
        address,
        provider,
        connectedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error connecting wallet:', error);
      throw error;
    }
  },
  
  async getWalletsByUser(userId) {
    try {
      const db = await initDB();
      const tx = db.transaction('wallets', 'readonly');
      const index = tx.store.index('userId');
      return index.getAll(userId);
    } catch (error) {
      console.error('Error getting wallets by user:', error);
      throw error;
    }
  },
  
  async disconnectWallet(id) {
    try {
      const db = await initDB();
      return db.delete('wallets', id);
    } catch (error) {
      console.error('Error disconnecting wallet:', error);
      throw error;
    }
  }
};

// Security monitoring operations
export const securityDB = {
  async logLoginAttempt(attempt) {
    try {
      const db = await initDB();
      return db.add('loginAttempts', {
        ...attempt,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error logging login attempt:', error);
      throw error;
    }
  },
  
  async getLoginAttemptsByEmail(email) {
    try {
      const db = await initDB();
      const tx = db.transaction('loginAttempts', 'readonly');
      const index = tx.store.index('email');
      return index.getAll(email);
    } catch (error) {
      console.error('Error getting login attempts by email:', error);
      throw error;
    }
  }
};

// Helper functions for password hashing (in a real app, use bcrypt)
async function hashPassword(password) {
  try {
    // This is a simplified version for demo
    // In production, use proper password hashing like bcrypt
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch (error) {
    console.error('Error hashing password:', error);
    throw error;
  }
}

async function verifyPassword(password, hashedPassword) {
  try {
    const hashedInput = await hashPassword(password);
    return hashedInput === hashedPassword;
  } catch (error) {
    console.error('Error verifying password:', error);
    throw error;
  }
} 