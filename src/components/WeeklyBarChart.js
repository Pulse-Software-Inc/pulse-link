'use client';

import React, { useEffect, useMemo, useState } from 'react';
//converter to number with null fallback
function toNum(x, fallback = 0) {
  if (typeof x === 'string') {
    x = x.replace(/,/g, '').trim();
  }
  const n = Number(x);
  return Number.isFinite(n) ? n : fallback;
}

function dayLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short' }); 
}
//to build barchart from jsonfile
export default function WeeklyBarChart({ jsonPath = '/userdata.json' }) {
  const [weekly, setWeekly] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setError('');
        const res = await fetch(jsonPath, { cache: 'no-store' });
        if (!res.ok) throw new Error(`Failed to load: ${jsonPath}`);
        const json = await res.json();
        const ws = json?.weekly_summary;
        console.log('weekly_summary', ws);
        if (!ws?.daily_steps?.length) throw new Error('weekly_summary.daily_steps missing');
        if (!cancelled) setWeekly(ws);
      } catch (e) {
        if (!cancelled) setError(e?.message || 'Failed to load weekly chart');
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [jsonPath]);
  const chartData = useMemo(() => {
    const daily = weekly?.daily_steps || [];
    return daily.map((d) => ({
      day: dayLabel(d.date),
      value: toNum(d.steps, 0),
      date: d.date,
    }));
  }, [weekly]);

//takes max value for steps
  const maxVal = useMemo(() => {
    const vals = chartData.map((d) => d.value);
    return Math.max(...vals, 1);
  }, [chartData]);

  if (error) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white shadow-[0_6px_0_rgba(0,0,0,0.06)] p-6 text-sm text-red-600">
        {error}
      </div>
    );
  }
  if (!weekly) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white shadow-[0_6px_0_rgba(0,0,0,0.06)] p-6">
        Loading chart...
      </div>
    );
  }

    //chart card ui
  return (
    <div className="relative rounded-2xl border border-gray-200 bg-white shadow-[0_6px_0_rgba(0,0,0,0.06)] p-6">
      <button
        type="button"
        aria-label="Next"
        className="absolute -right-4 top-1/2 -translate-y-1/2 h-9 w-9 rounded-full border border-gray-200 bg-white shadow flex items-center justify-center hover:bg-gray-50"
      >
        <span className="text-gray-700">›</span>
      </button>
      <div className="h-[220px] flex items-end gap-4 px-2 pt-6 pb-2">
        <div className="h-full w-12 flex flex-col justify-between text-[10px] text-gray-400">
          <span>{Math.round((maxVal * 1.0) / 1000) * 1000}</span>
          <span>{Math.round((maxVal * 0.75) / 1000) * 1000}</span>
          <span>{Math.round((maxVal * 0.5) / 1000) * 1000}</span>
          <span>{Math.round((maxVal * 0.25) / 1000) * 1000}</span>
          <span>0</span>
        </div>
        <div className="relative h-full flex-1">
          <div className="absolute inset-0 pointer-events-none">
            <div className="h-full w-full border border-dashed border-gray-100 rounded-lg" />
            <div className="absolute left-0 right-0 top-1/4 border-t border-dashed border-gray-100" />
            <div className="absolute left-0 right-0 top-1/2 border-t border-dashed border-gray-100" />
            <div className="absolute left-0 right-0 top-3/4 border-t border-dashed border-gray-100" />
          </div>
          <div className="relative h-full flex items-end justify-between gap-4 px-3">
            {chartData.map((d) => {
              const MAX_BAR_PX = 160; 
              const h = Math.max(3, (d.value / maxVal) * MAX_BAR_PX);
              return (
                <div key={d.date} className="flex flex-col items-center gap-2 flex-1">
                  <div
                    className="w-full max-w-[54px] rounded-lg bg-blue-500"
                    style={{ height: `${h}px` }}
                    title={`${d.date}: ${d.value}`}
                  />
                  <div className="text-[10px] text-gray-500">{d.day}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <div className="mt-2 grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-[10px] text-gray-400">Average Steps</div>
          <div className="text-sm text-gray-700 font-medium">
            {toNum(weekly.average_steps, 0).toLocaleString()}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400">Total Distance</div>
          <div className="text-sm text-gray-700 font-medium">
            {toNum(weekly.total_distance_km, 0)} km
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400">Active Days</div>
          <div className="text-sm text-gray-700 font-medium">
            {toNum(weekly.active_days, 0)}/7
          </div>
        </div>
      </div>

      {/* Slider dots
      <div className="mt-5 flex items-center justify-center gap-2">
        <span className="h-2 w-2 rounded-full bg-gray-300" />
        <span className="h-2 w-2 rounded-full bg-[#71E4FD]" />
        <span className="h-2 w-2 rounded-full bg-gray-300" />
      </div> */}
      
    </div>
  );
}