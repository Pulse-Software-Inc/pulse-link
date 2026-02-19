'use client';
import React from 'react';
import doctorSidebar from '@/components/doctorDB_siderbar';
import Image from 'next/image';

function doctorDashboard() {
    return (
        <div className="flex min-h-screen">
            <doctorSidebar />
            <div className="flex-1 bg-white">
                {/* Header */}
                <header className="flex items-center justify-between px-8 py-3 mx-5 border-b border-gray-400">
                    <h1 className="text-3xl font-semibold text-gray-900">Welcome Doctor!</h1>
                    <Image 
                        src="/PulseLink_logo.svg" 
                        alt="Pulse Link Logo" 
                        width={100} 
                        height={100}
                    />
                </header>
                {/* Main content area */}
            </div>
        </div>
    );
}

export default doctorDashboard;
