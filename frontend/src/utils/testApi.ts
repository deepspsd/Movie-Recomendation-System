// Quick API connectivity test
// Run this in browser console: import('./utils/testApi').then(m => m.testConnection())

export const testConnection = async () => {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  
  console.log('Testing API connection...');
  console.log('API URL:', API_URL);
  
  try {
    // Test health endpoint
    const healthResponse = await fetch('http://localhost:8000/health');
    console.log('✅ Health check:', healthResponse.status, await healthResponse.json());
    
    // Test registration endpoint
    const testData = {
      username: 'frontendtest',
      email: 'frontendtest@example.com',
      password: 'Password123'
    };
    
    console.log('Testing registration with:', testData);
    const registerResponse = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData)
    });
    
    console.log('Registration status:', registerResponse.status);
    const data = await registerResponse.json();
    console.log('Registration response:', data);
    
    if (registerResponse.ok) {
      console.log('✅ Registration works!');
    } else {
      console.error('❌ Registration failed:', data);
    }
  } catch (error) {
    console.error('❌ Connection error:', error);
  }
};
