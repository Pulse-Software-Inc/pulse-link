'use client';
import React, { useEffect, useState } from "react";
import doctorSidebarData from "./ProfessionalSideBarData";
import Image from "next/image";
import Link from "next/link";

function DoctorSidebar() {
    const [name, setName] = useState('Doctor not found');
    const [email, setEmail] = useState('Email not found');
    const [open, openSet] = useState(false);
    const [isDesktop, setIsDesktop] = useState(false);

    const ToggleButton = ({ className, label = 'Toggle sidebar' }) => (
        <button
            type="button"
            aria-label={label}
            onClick={() => openSet((v) => !v)}
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

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const mediaQuery = window.matchMedia('(min-width: 1024px)');
        const syncSidebarMode = (mq) => {
            const desktopMode = mq.matches;
            setIsDesktop(desktopMode);
            openSet(desktopMode);
        };

        syncSidebarMode(mediaQuery);

        const handleChange = (event) => {
            syncSidebarMode(event);
        };

        if (typeof mediaQuery.addEventListener === 'function') {
            mediaQuery.addEventListener('change', handleChange);
            return () => mediaQuery.removeEventListener('change', handleChange);
        }

        mediaQuery.addListener(handleChange);
        return () => mediaQuery.removeListener(handleChange);
    }, []);

    if (isDesktop && !open) {
        return (
            <div className="flex w-16 min-h-screen flex-col items-center bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] pt-5 shadow-lg">
                <ToggleButton label="Expand sidebar" className="flex flex-col gap-1 rounded-lg border border-gray-200 bg-white p-3 shadow" />
            </div>
        );
    }


    return (
        <>
            {!isDesktop && !open ? (
                <div className="fixed left-4 top-4 z-50">
                    <ToggleButton
                        label="Open sidebar"
                        className="flex flex-col gap-1 rounded-lg border border-gray-200 bg-white/95 p-3 shadow"
                    />
                </div>
            ) : null}

            {!isDesktop && open ? (
                <button
                    type="button"
                    aria-label="Close sidebar overlay"
                    onClick={() => openSet(false)}
                    className="fixed inset-0 z-40 bg-black/30"
                />
            ) : null}

            <aside
                className={`flex flex-col bg-[linear-gradient(to_bottom,#71E4FD,#B2C4FE,#D3B5FF,#ECB6E6)] p-4 shadow-lg transition-transform duration-300 sm:p-5 lg:min-h-screen lg:w-56 lg:p-6 ${
                    isDesktop
                        ? 'relative'
                        : `fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] ${open ? 'translate-x-0' : '-translate-x-full'}`
                }`}
            >
                {/* User Profile Section */}
                <div className="mb-4 flex items-start justify-between gap-3 lg:mb-6">
                    <div className="flex items-center gap-3">
                        <img src="/Sidebar/Dashboard_Icon.svg" alt="User" className="w-12 h-12 rounded-full bg-gray-300" />
                        <div className="flex flex-col">
                            <h3 className="max-w-[12rem] truncate text-sm font-semibold text-white sm:text-base">{name}</h3>
                            <p className="max-w-[12rem] truncate text-xs text-white opacity-90">{email}</p>
                        </div>
                    </div>
                    <ToggleButton
                        label={open ? 'Collapse sidebar' : 'Expand sidebar'}
                        className="flex flex-col gap-1 rounded-lg border border-white/50 bg-white/80 p-2 shadow hover:bg-white"
                    />
                </div>

                <hr className="mb-4 border-gray-500/70 lg:mb-6" />

                {/* Navigation Menu */}
                <nav className="space-y-2 overflow-y-auto pb-2">
                    {doctorSidebarData.map((val, key) => (
                        <Link
                            key={key}
                            href={val.link}
                            onClick={() => {
                                if (!isDesktop) openSet(false);
                            }}
                            className="flex items-center gap-3 rounded-lg px-4 py-3 text-left text-white transition-all hover:bg-white/20 lg:w-full"
                        >
                            <span className="text-xl">{val.icon}</span>
                            <span className="font-medium">{val.title}</span>
                        </Link>
                    ))}

                    {/* Sign Out Button */}
                    <Link
                        href="/auth/signout"
                        onClick={() => {
                            if (!isDesktop) openSet(false);
                        }}
                        className="flex items-center gap-3 rounded-lg px-4 py-3 font-semibold text-red-500 transition-all hover:bg-white/20 lg:w-full"
                    >
                        <Image src="/Sidebar/LogOut_Icon.svg" alt="Sign out" width={24} height={24} />
                        <span>Sign out</span>
                    </Link>
                </nav>
            </aside>
        </>
    );
}

export default DoctorSidebar; 