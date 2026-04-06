'use client';
import React from 'react';
import Sidebar from '@/components/nav/SideBar';
import Image from 'next/image';
import DB_card from '@/components/dashboard/DashCards';
import useDB_cardsData from '@/components/dashboard/DashCardsData';
import WeeklyBarChart from '@/components/WeeklyBarChart';

function UserDashboard() {
    //fetches the data for the cards from public/userdata.json and formats it for the cards.
    const { cards, loading, error } = useDB_cardsData('/userdata.json', 10000, 2550);
    
    //making variables to display date and time
    const nowatm = new Date();
    const dateStr = nowatm.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = nowatm.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    return (
        <div className="flex min-h-screen flex-col lg:flex-row bg-gray-50">
            <Sidebar />
            <div className="flex-1 bg-white lg:min-w-0">
                {/* Header */}
                <header className="flex items-center justify-between border-b border-gray-300 py-3 pl-16 pr-4 sm:px-6 lg:px-8">
                    <h1 className="pr-3 text-xl font-semibold leading-tight text-gray-900 sm:text-2xl lg:text-3xl">Welcome User!</h1>
                    <Image 
                        src="/PulseLink_logo.svg" 
                        alt="Pulse Link Logo" 
                        width={72} 
                        height={72}
                        className="h-11 w-11 sm:h-14 sm:w-14 lg:h-[72px] lg:w-[72px]"
                    />
                </header>
                {/* Main content area */}
                <main className="px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
                    <div className="mx-auto w-full max-w-7xl">
                        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                            <span className="rounded-full bg-gray-100 px-3 py-1 text-[11px] text-gray-900 sm:text-xs">{dateStr}</span>
                            <span className="rounded-full bg-gray-100 px-3 py-1 text-[11px] text-gray-900 sm:text-xs">{timeStr}</span>
                        </div>

                        {/*Display Cards*/}
                        <div className="mt-5 grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 xl:grid-cols-3">
                            {loading ? (<>
                                <div className="mt-1 min-h-[190px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                                <div className="mt-1 min-h-[190px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                                <div className="mt-1 min-h-[190px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                            </>
                            ) : error ? (
                                <div className="col-span-full text-sm text-red-600">{error}</div>
                            ) : (
                                (cards || []).map((val) => <DB_card key={val.id} val={val} />)
                            )}
                        </div>
                        <div className="mt-8 grid grid-cols-1 items-stretch gap-6 lg:gap-8 xl:mt-10 xl:grid-cols-[1fr_320px]">
                            <WeeklyBarChart jsonPath="/userdata.json" />
                            <div className="flex min-h-[220px] items-center justify-center rounded-2xl border border-transparent bg-white sm:min-h-[320px]">
                                {/* mascot */}
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default UserDashboard;
