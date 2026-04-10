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
        <div className="flex min-h-screen flex-col lg:flex-row bg-gray-50">
            <DoctorSidebar />
            <div className="flex-1 bg-white lg:min-w-0">
                {/* Header */}
                <header className="flex items-center justify-between border-b border-gray-300 py-3 pl-16 pr-4 sm:px-6 lg:px-8">
                    <h1 className="pr-3 text-xl font-semibold leading-tight text-gray-900 sm:text-2xl lg:text-3xl">Welcome {providerName}</h1>
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
                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 xl:grid-cols-3 xl:gap-8">
                        {loading ? (
                            <>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                                <div className="rounded-2xl border border-gray-200 bg-white p-5 min-h-[220px]">Loading...</div>
                            </>
                        ) : error ? (
                            <div className="col-span-full text-sm text-red-600">{error}</div>
                        ) : (
                            (cards || []).map((val) => <DB_card key={val.id} val={val} />)
                        )}
                    </div>


                    <div className="mt-6 sm:mt-8">
                        <ListOfPatients loading={loading} error={error} clients={clients} />
                    </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default DoctorDashboard;
