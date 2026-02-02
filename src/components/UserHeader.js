import React from 'react';

export default function UserHeader() {

  return (
    <header style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
      <img 
        src="/PulseLink_logo.svg" 
        alt="PulseLink Logo" 
        style={{ height: '125px', width: 'auto' }}
      />
      <span style={{ fontSize: '24px', fontWeight: 'normal', color: '#fffafa' }}>PulseLink</span>
    </header>
  );
}