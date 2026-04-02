'use client';
import React from 'react';
import DoctorSidebar from '@/components/nav/ProfessionalSideBar';
import Image from 'next/image';
import DB_card from '@/components/dashboard/ProfessionalDashCards';
import useDoctorDB_cardsData from '@/components/dashboard/ProfessionalDashCardsData';
import ListOfPatients from '@/components/listOfPatients';

function DoctorDashboard() {
    const { cards, clients, providerName, loading, error } = useDoctorDB_cardsData('/prodata.json');

    return (
        <div className="flex min-h-screen">
            <DoctorSidebar />
            <div className="flex-1 bg-white">
                {/* Header */}
                <header className="flex items-center justify-between px-4 py-3 mx-0 md:mx-5 border-b border-gray-400">
                    <h1 className="text-3xl font-semibold text-gray-900">Welcome {providerName}</h1>
                    <Image
                        src="/PulseLink_logo.svg"
                        alt="Pulse Link Logo"
                        width={80}
                        height={80}
                    />
                </header>

                {/* Main content area */}
                <main className="px-4 md:px-8 py-6 mx-0 md:mx-5">
                    <div className="w-full max-w-6xl mx-auto">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 md:gap-10">
                        {loading ? (
                            <>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                            </>
                        ) : error ? (
                            <div className="text-red-600 text-sm col-span-3">{error}</div>
                        ) : (
                            (cards || []).map((val) => <DB_card key={val.id} val={val} />)
                        )}
                    </div>

                    
                    <ListOfPatients loading={loading} error={error} clients={clients} />
                    </div>
                </main>
            </div>
        </div>
    );
}

export default DoctorDashboard;
