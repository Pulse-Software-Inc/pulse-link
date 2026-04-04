'use client';
import React, { useEffect, useState } from "react";
import doctorSidebarData from "./ProfessionalSideBarData";
import Image from "next/image";
import Link from "next/link";

function DoctorSidebar() {
    const [name, setName] = useState('Doctor not found');
    const [email, setEmail] = useState('Email not found');
    const [open, openSet] = useState(true);

    const ToggleButton= ({ className }) => (
        <button
            type="button"
            aria-label="Toggle sidebar"
            onClick={()=>openSet((v)=>!v)}
            className={className}
        >
            <span className="block w-5 h-[2px] bg-gray-700 rounded"/>
            <span className="block w-5 h-[2px] bg-gray-700 rounded" />
            <span className="block w-5 h-[2px] bg-gray-700 rounded" />
        </button>
    );
    useEffect(() => {
        fetch('/prodata.json', { cache: 'no-store' })
            .then(res => res.json())
            .then(data => {
                const profile = data?.provider_profile || {};
                setName(profile.name || 'Doctor not found');
                setEmail(data?.provider_email || profile.email || '');
            })
            .catch(() => {});
    }, []);

     if (!open) {
         return (
             <div className="w-16 min-h-screen bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] flex flex-col items-center pt-5 shadow-lg">
                 <ToggleButton className="flex flex-col gap-1 p-3 rounded-lg bg-white shadow border border-gray-200" />
             </div>);
    }


    return (
        <div className="relative w-56 min-h-screen bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] flex flex-col p-6 shadow-lg">
            {/* User Profile Section */}
            <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-3">
                    <img src="/Dashboard_Icon.svg" alt="User" className="w-12 h-12 rounded-full bg-gray-300" />
                        <div className="flex flex-col">
                            <h3 className="text-white font-semibold text-base">{name}</h3>
                            <p className="text-white text-xs opacity-90">{email}</p>
                        </div>
                </div> 
                <ToggleButton className="flex flex-col gap-1 p-2 rounded-lg bg-white/80 hover:bg-white shadow border border-white/50" />
            </div>
            
            <hr className="border-gray-500 mb-6" />
            {/* Navigation Menu */}
            <nav className="space-y-2">
                {doctorSidebarData.map((val, key) => (
                    <Link
                        key={key}
                        href={val.link}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-white transition-all hover:bg-white/20 text-left"
                    >
                        <span className="text-xl">{val.icon}</span>
                        <span className="font-medium">{val.title}</span>
                    </Link>
                ))}

                {/* Sign Out Button */}
                <Link href="/auth/signout" className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-500 font-semibold hover:bg-white/20 transition-all">
                    <Image src="/Sidebar/LogOut_Icon.svg" alt="Sign out" width={24} height={24} />
                    <span>Sign out</span>
                </Link>
            </nav>
        </div>
    );
}

export default DoctorSidebar; 