/*Creating dashboard cards to be reused in  doctor dashboard page. */
'use client';

import React from 'react';
import Image from 'next/image';

function clamp(x, min, max) {
    return Math.max(min, Math.min(max, x));
}

function ProgressBar({ value = 0, max = 100 }) {
    const safeMax = max == 0 ? 1 : max;
    const percen = clamp((value / safeMax) * 100, 0, 100);
    
    return (
        <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden">
            <div
                className="h-full rounded-full"
                style={{
                width: `${percen}%`,
                background: `linear-gradient(to right, #71E4FD, #B2C4FE, #D3B5FF, #ECB6E6)`
            }}
            />
        </div>
    ); 
}

//Main Card
export default function DB_card({ val }) {
    return (
        <div className="rounded-2xl border border-gray-300 shadow-sm p-5 min-h-[210px]">
            <div className="flex h-full flex-col justify-between">
                <div className="flex items-start justify-between">
                    <h3 className="text-[24px] font-medium leading-none text-gray-900">{val.title}</h3>

                    <Image
                        src={val.iconSrc}
                        alt={`${val.title} Icon`}
                        width={24}
                        height={24}
                        className="h-6 w-6 opacity-70"
                    />
                </div>

                <div>
                    <div className="text-gray-900">
                        <span className="text-4xl font-medium leading-none">{val.main}</span>
                    </div>

                    {val.sub ? <div className="mt-1 text-xl text-gray-500">{val.sub.trim()}</div> : null}

                    {val.progress ? (
                        <div className="mt-3">
                            <ProgressBar value={val.progress.value} max={val.progress.max} />
                        </div>
                    ) : null}

                    {val.footer ? <div className="mt-3 text-xs text-gray-500">{val.footer}</div> : null}
                </div>
            </div>
        </div>

    );
}
