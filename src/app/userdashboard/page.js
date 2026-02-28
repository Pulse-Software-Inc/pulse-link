'use client';
import React from 'react';
import Sidebar from '@/components/Sidebar';
import Image from 'next/image';
import DB_card from '@/components/DB_cards';
import useDB_cardsData from '@/components/DB_cardsData';

function UserDashboard() {
    //fetches the data for the cards from public/userdata.json and formats it for the cards.
    const { cards, loading, error } = useDB_cardsData('/userdata.json', 10000, 2550);
    
    //making variables to display date and time
    const nowatm = new Date();
    const dateStr = nowatm.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = nowatm.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 bg-white">
                {/* Header */}
                <header className="flex items-center justify-between px-8 py-3 mx-5 border-b border-gray-400">
                    <h1 className="text-3xl font-semibold text-gray-900">Welcome User!</h1>
                    <Image 
                        src="/PulseLink_logo.svg" 
                        alt="Pulse Link Logo" 
                        width={100} 
                        height={100}
                    />
                </header>
                {/* Main content area */}
                <main className="px-8 py-6 mx-5">
                    <div className="flex items-center gap-3">
                        <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-900 text-xs">{dateStr}</span>
                        <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-900 text-xs">{timeStr}</span>
                    </div>

                    {/*Display Cards*/}
                    <div className="mt-5 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {loading ? (<>
                            <div className="rounded-2xl border border-gray-200 bg-white p-5 mt-6">Loading...</div>
                            <div className="rounded-2xl border border-gray-200 bg-white p-5 mt-6">Loading...</div>
                            <div className="rounded-2xl border border-gray-200 bg-white p-5 mt-6">Loading...</div>    
                        </>
                        ) : error ? (
                            <div className="text-red-600 text-sm">{error}</div>
                        ) : (
                            (cards || []).map((val) => <DB_card key={val.id} val={val} />)
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}

export default UserDashboard;
