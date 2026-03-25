'use client';
import React from 'react';
import DoctorSidebar from '@/components/doctorDB_siderbar';
import Image from 'next/image';
import DB_card from '@/components/doctorDB_cards';
import useDoctorDB_cardsData from '@/components/doctorDB_cardsData';
import ListOfPatients from '@/components/listOfPatients';

function DoctorDashboard() {
    const { cards, clients, providerName, loading, error } = useDoctorDB_cardsData('/prodata.json');

    return (
        <div className="flex min-h-screen">
            <DoctorSidebar />
            <div className="flex-1 bg-white">
                {/* Header */}
                <header className="flex items-center justify-between px-8 py-3 mx-5 border-b border-gray-400">
                    <h1 className="text-3xl font-semibold text-gray-900">Welcome {providerName}</h1>
                    <Image
                        src="/PulseLink_logo.svg"
                        alt="Pulse Link Logo"
                        width={100}
                        height={100}
                    />
                </header>

                {/* Main content area */}
                <main className="px-8 py-6 mx-5">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-3 gap-14">
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
                </main>
            </div>
        </div>
    );
}

export default DoctorDashboard;
