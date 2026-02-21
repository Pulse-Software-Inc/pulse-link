/*Creating dashboard cards to be reused in the user dashboard page and 
doctor dashboard page. */
'use client';

import React from 'react';
import Image from 'next/image';

function clamp(x, min, max) {
    return Math.max(min, Math.min(max, x));
}

function ProgressBar({ value = 0, max = 100 }) {
    const safeMax = max == 0 ? 1 : max;
    const percen = clamp((value / max) * 100, 0, 100);
    
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
        //icon and title at the top.
        <div className="rounded-2xl border border-gray-200 bg-white shadow-[0_6px_0_rgba(0,0,0,0.06)] p-5">
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                    <Image
                        src={val.iconSrc}
                        alt={`${val.title} Icon `}
                        width={20}
                        height={20}
                        className="w-5 h-5"
                    />
                    
                    <h3 className="font-semibold text-gray-800">{val.title}</h3>
                </div>
                {/*just includes the value, progress and footer*/}
                <div className="mt-4">
                    <div className="text-gray-900">
                        <span className="text-2xl font-semibold">{val.main}</span>
                        {val.sub ? <span className="text-sm text-gray-500">{val.sub}</span> : null}
                    </div>
                    
                    {val.progress ? (
                        <div className="mt-3">
                            <progressBar value={val.progress.value} max={val.progress.max} />
                            </div>
                    ) : null}

                    {val.footer ? <div className="mt-3 text-xs text-gray-500">{val.footer}</div> : null}
                </div>
            </div>
        </div>

    );
}
