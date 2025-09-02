import React, { useState } from 'react';

const TestLogin = () => {
  const [result, setResult] = useState('');

  const testDirectLogin = async () => {
    try {
      // Direct API call to test login
      const response = await fetch('http://localhost:8002/api/v1/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=admin&password=admin123'
      });
      
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
      
      if (data.status_code === 200) {
        // Store token and redirect
        localStorage.setItem('access_token', data.data.access_token);
        alert('Login successful! Token stored.');
        window.location.href = '/dashboard';
      }
    } catch (error) {
      setResult('Error: ' + error.message);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Direct Login Test</h1>
      <button onClick={testDirectLogin} style={{ 
        padding: '10px 20px', 
        fontSize: '16px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        Test Direct Login (admin/admin123)
      </button>
      <pre style={{ 
        marginTop: '20px', 
        padding: '10px', 
        backgroundColor: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '4px',
        whiteSpace: 'pre-wrap'
      }}>
        {result}
      </pre>
    </div>
  );
};

export default TestLogin;