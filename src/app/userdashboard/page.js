'use client';
import React from 'react';
import Sidebar from '@/components/Sidebar';

function UserDashboard() {
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 bg-white">
                {/* Main content area */}
            </div>
        </div>
    );
}

export default UserDashboard;
