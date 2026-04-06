'use client';
import React from 'react';
import Sidebar from '@/components/nav/SideBar';
import Image from 'next/image';
import DB_card from '@/components/dashboard/DashCards';
import useDB_cardsData from '@/components/dashboard/DashCardsData';
import WeeklyBarChart from '@/components/WeeklyBarChart';
import MascotPanel from '@/components/nav/MascotPanel';
import ChatBox from '@/components/dashboard/ChatBox';

function UserDashboard() {
    //fetches the data for the cards from public/userdata.json and formats it for the cards.
    const { cards, loading, error } = useDB_cardsData('/userdata.json', 10000, 2550);
    
    //percentage calculations to decide what mascot to show.
    const stepsCard = (cards || []).find((c) => c.id === 'Steps');
    const kcalCard = (cards || []).find((c) => c.id === 'Kcal');
    const stepsPct = stepsCard?.progress ? (stepsCard.progress.value / stepsCard.progress.max) * 100 : 0;
    const caloriesPct = kcalCard?.progress ? (kcalCard.progress.value / kcalCard.progress.max) * 100 : 0;

    //making variables to display date and time
    const nowatm = new Date();
    const dateStr = nowatm.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = nowatm.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    const syncTimeCard =
        !loading && !error
            ? (cards || []).find((c) => typeof c.footer === 'string' && c.footer.includes('Last sync:'))?.footer : null;
    const lastSync=syncTimeCard ?syncTimeCard.replace(/\s+/g,' ').trim():'Last sync: —';
    return (
        <div className="flex min-h-screen flex-col lg:flex-row bg-gray-50">
            <Sidebar />
            <div className="flex flex-col flex-1 bg-white lg:min-w-0">
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
                <main className="flex flex-col flex-1 px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
                    <div className="flex flex-col flex-1 mx-auto w-full max-w-7xl gap-4">
                        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                            <span className="rounded-full bg-gray-100 px-3 py-1 text-[11px] text-gray-900 sm:text-xs">{dateStr}</span>
                            <span className="rounded-full bg-gray-100 px-3 py-1 text-[11px] text-gray-900 sm:text-xs">{timeStr}</span>
                            <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-900 text-xs whitespace-nowrap">{lastSync}</span>
                        </div>

                        {/*Display Cards*/}
                        <div className="flex-1 grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6 xl:gap-8 items-stretch">
                            <div className="flex flex-col gap-5 justify-between">

                        <div className="grid grid-cols-1 gap-4 sm:gap-5 md:grid-cols-2 xl:grid-cols-3">
                            {loading ? (<>
                                <div className="mt-1 min-h-[100px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                                <div className="mt-1 min-h-[100px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                                <div className="mt-1 min-h-[100px] rounded-2xl border border-gray-200 bg-white p-5">Loading...</div>
                            </>
                            ) : error ? (
                                <div className="col-span-full text-sm text-red-600">{error}</div>
                            ) : (
                                (cards || []).map((val) => <DB_card key={val.id} val={val} />)
                            )}
                            </div>
                            <div className="flex-1">
                            <WeeklyBarChart jsonPath="/userdata.json" />
                        </div>
                            </div>
                        <div className="hidden xl:flex items-center justify-center h-full w-full relative">
                                <MascotPanel stepsPct={stepsPct} caloriesPct={caloriesPct} />
                                <ChatBox />
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default UserDashboard;
