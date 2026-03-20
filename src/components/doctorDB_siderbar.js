import React, { useEffect, useState } from "react";
import doctorSidebarData from "./doctorDB_sidebarData";
import { Avatar } from '@mui/material';
import Image from "next/image";
import Link from "next/link";

function DoctorSidebar() {
    const [name, setName] = useState('Doctor not found');
    const [email, setEmail] = useState('Email not found');

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
    return (
        <div className="w-54 min-h-screen bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] flex flex-col p-6 shadow-lg">
                {/* User Profile Section */}
            <div className="flex flex-row items-center gap-3 mb-8">
                <Avatar
                    sx={{
                        width: 48,
                        height: 48,
                        bgcolor: 'white',
                        color: '#9333ea',
                        fontSize: '1.2rem',
                        fontWeight: 'bold'
                    }}
                >
                    JD
                </Avatar>
                <div className="flex flex-col">
                    <h3 className="text-white font-semibold text-base">{name}</h3>
                    <p className="text-white text-xs opacity-90">{email}</p>
                </div>
            </div>
            <hr className="border-gray-500 mb-6" />
            {/* Navigation Menu */}
            <nav className="space-y-2">
                {doctorSidebarData.map((val, key) => (
                    <button
                        key={key}
                        onClick={() => { window.location.pathname = val.link }}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-white transition-all hover:bg-white/20 text-left"
                    >
                        <span className="text-xl">{val.icon}</span>
                        <span className="font-medium">{val.title}</span>
                    </button>
                ))}

                {/* Sign Out Button */}
                <Link href="/auth/signout" className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-500 font-semibold hover:bg-white/20 transition-all">
                    <Image src="/LogOut_Icon.svg" alt="Sign out" width={24} height={24} />
                    <span>Sign out</span>
                </Link>
            </nav>
        </div>
    );
}

export default DoctorSidebar; 