/**
 * Secure Local Storage Utility
 * Handles storage with expiration and encryption-ready structure
 */

interface StorageItem<T> {
  value: T;
  expiry?: number;
  timestamp: number;
}

class SecureStorage {
  private prefix: string;

  constructor(prefix: string = 'movie_app_') {
    this.prefix = prefix;
  }

  /**
   * Set item in storage with optional expiration
   */
  set<T>(key: string, value: T, expiryMinutes?: number): void {
    try {
      const item: StorageItem<T> = {
        value,
        timestamp: Date.now(),
        expiry: expiryMinutes ? Date.now() + expiryMinutes * 60 * 1000 : undefined,
      };

      localStorage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  /**
   * Get item from storage
   */
  get<T>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(this.prefix + key);
      if (!itemStr) return null;

      const item: StorageItem<T> = JSON.parse(itemStr);

      // Check if expired
      if (item.expiry && Date.now() > item.expiry) {
        this.remove(key);
        return null;
      }

      return item.value;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  }

  /**
   * Remove item from storage
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(this.prefix + key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  }

  /**
   * Clear all items with prefix
   */
  clear(): void {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach((key) => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }

  /**
   * Check if item exists and is not expired
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Get all keys with prefix
   */
  keys(): string[] {
    try {
      const keys = Object.keys(localStorage);
      return keys
        .filter((key) => key.startsWith(this.prefix))
        .map((key) => key.replace(this.prefix, ''));
    } catch (error) {
      console.error('Error getting keys from localStorage:', error);
      return [];
    }
  }

  /**
   * Get storage size in bytes
   */
  getSize(): number {
    try {
      let size = 0;
      const keys = Object.keys(localStorage);
      keys.forEach((key) => {
        if (key.startsWith(this.prefix)) {
          const item = localStorage.getItem(key);
          if (item) {
            size += item.length + key.length;
          }
        }
      });
      return size;
    } catch (error) {
      console.error('Error calculating storage size:', error);
      return 0;
    }
  }

  /**
   * Clean expired items
   */
  cleanExpired(): number {
    try {
      let cleaned = 0;
      const keys = this.keys();
      
      keys.forEach((key) => {
        const itemStr = localStorage.getItem(this.prefix + key);
        if (itemStr) {
          try {
            const item: StorageItem<any> = JSON.parse(itemStr);
            if (item.expiry && Date.now() > item.expiry) {
              this.remove(key);
              cleaned++;
            }
          } catch {
            // Invalid item, remove it
            this.remove(key);
            cleaned++;
          }
        }
      });

      return cleaned;
    } catch (error) {
      console.error('Error cleaning expired items:', error);
      return 0;
    }
  }
}

// Export singleton instance
export const storage = new SecureStorage();

// Export class for custom instances
export { SecureStorage };

// Specific storage helpers
export const authStorage = {
  setTokens: (accessToken: string, refreshToken: string) => {
    storage.set('access_token', accessToken, 30); // 30 minutes
    storage.set('refresh_token', refreshToken, 10080); // 7 days
  },
  
  getAccessToken: () => storage.get<string>('access_token'),
  
  getRefreshToken: () => storage.get<string>('refresh_token'),
  
  clearTokens: () => {
    storage.remove('access_token');
    storage.remove('refresh_token');
  },
};

export const userPreferences = {
  setTheme: (theme: 'light' | 'dark' | 'system') => {
    storage.set('theme', theme);
  },
  
  getTheme: () => storage.get<'light' | 'dark' | 'system'>('theme') || 'system',
  
  setLanguage: (lang: string) => {
    storage.set('language', lang);
  },
  
  getLanguage: () => storage.get<string>('language') || 'en',
};
