import React from 'react';

export default function UserHeader() {

  return (
    <header style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
      <img
        src="/PulseLink_logo.svg"
        alt="PulseLink Logo"
        style={{ height: '125px', width: 'auto' }}
      />
      <span style={{ fontSize: '30px', fontWeight: 'bold', color: '#fffafa' }}>PulseLink</span>
    </header>
  );
}