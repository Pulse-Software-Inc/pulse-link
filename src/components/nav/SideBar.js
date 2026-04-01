'use client';
import React, { use, useState } from "react";
import SidebarData from "./SideBarData";
import { Avatar } from '@mui/material';
import Image from "next/image";
import {useRouter} from "next/navigation";

function Sidebar() {
    const [open, openSet] = useState(true);
    const router = useRouter();

    //toggle button for sidebar
    const ToggleButton = ({ className }) => (
        <button
            type="button"
            aria-label="Toggle sidebar"
            onClick={() => openSet((v) => !v)}
            className={className}
        >
            <span className="block w-5 h-[2px] bg-gray-700 rounded"/>
            <span className="block w-5 h-[2px] bg-gray-700 rounded" />
            <span className="block w-5 h-[2px] bg-gray-700 rounded" />
        </button>
    );
    //closed view for the button
    if (!open) {
        return (
        <div className="w-16 min-h-screen bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] flex flex-col items-center pt-5 shadow-lg">
            <ToggleButton className="flex flex-col gap-1 p-3 rounded-lg bg-white shadow border border-gray-200" />
        </div>
        );
    }

    return (
        <div className="relative w-54 min-h-screen bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] flex flex-col p-6 shadow-lg">
                {/* User Profile Section */}
            <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Avatar
                        sx={{
                            width: 48,
                            height: 48,
                            bgcolor: 'white',
                            color: '#9333ea',
                            fontSize: '1.2rem',
                            fontWeight: 'bold',
                            }}
                        >
                            U1
                        </Avatar>

                        <div className="flex flex-col">
                            <h3 className="text-white font-semibold text-base">User 1</h3>
                            <p className="text-white text-xs opacity-90">user1@puls.com</p>
                        </div>
                    </div>

  <ToggleButton className="flex flex-col gap-1 p-2 rounded-lg bg-white/80 hover:bg-white shadow border border-white/50" />
</div>

            {/* Navigation Menu */}
            <nav className="space-y-2">
                {SidebarData.map((val, key) => (
                    <button
                        key={key}
                        onClick={() => router.push(val.link)}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-white transition-all hover:bg-white/20 text-left"
                    >
                        <span className="text-xl">{val.icon}</span>
                        <span className="font-medium">{val.title}</span>
                    </button>
                ))}
            
                {/* Sign Out Button */}
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-500 font-semibold hover:bg-white/20 transition-all">
                    <Image src="/LogOut_Icon.svg" alt="Sign out" width={24} height={24} />
                    <span>Sign out</span>
                </button>
            </nav>
        </div>
    );
}

export default Sidebar; 