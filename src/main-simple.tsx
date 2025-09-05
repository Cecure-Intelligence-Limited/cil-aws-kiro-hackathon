// import React from 'react';
import ReactDOM from 'react-dom/client';

// Simple test component
function SimpleApp() {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      background: '#1a1a1a',
      color: 'white',
      minHeight: '100vh'
    }}>
      <h1>🚀 Aura Desktop Assistant</h1>
      <p>React is working!</p>
      <div style={{ 
        background: '#333', 
        padding: '20px', 
        borderRadius: '10px',
        marginTop: '20px'
      }}>
        <h2>Test Interface</h2>
        <input 
          type="text" 
          placeholder="Type a command here..." 
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '10px',
            borderRadius: '5px',
            border: '1px solid #555',
            background: '#222',
            color: 'white'
          }}
        />
        <button style={{
          background: '#007acc',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '5px',
          cursor: 'pointer'
        }}>
          Send Command
        </button>
      </div>
    </div>
  );
}

// Initialize React app
const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(<SimpleApp />);