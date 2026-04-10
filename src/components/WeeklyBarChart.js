'use client';
import React, { useEffect, useMemo, useState } from 'react';
// import { useAuth } from "@/lib/maintainSessionToken.js"

function toNum(x, fallback = 0) {
  if (typeof x === 'string') x = x.replace(/,/g, '').trim();
  const n = Number(x);
  return Number.isFinite(n) ? n : fallback;
}

function dayLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short' });
}

function buildHeartRatePaths(points, yMin, yMax) {
  const W = 1000;
  const H = 260;
  const padL = 70;
  const padR = 30;
  const padT = 20;
  const padB = 45;

  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const n = points.length || 1;

  const xAt = (i) => padL + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
  const yAt = (v) => {
    const t = (v - yMin) / (yMax - yMin || 1);
    const clamped = Math.max(0, Math.min(1, t));
    return padT + (1 - clamped) * plotH;
  };

  const coords = points.map((p, i) => ({
    x: xAt(i),
    y: yAt(toNum(p.bpm, yMin)),
    label: p.label,
    bpm: toNum(p.bpm, yMin),
  }));
  const line = coords
    .map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`)
    .join(' ');

  const baseY = padT + plotH;
  const area = `${line} L ${coords[coords.length - 1].x.toFixed(1)} ${baseY.toFixed(1)} L ${coords[0].x.toFixed(
    1
  )} ${baseY.toFixed(1)} Z`;

  return { W, H, padL, padR, padT, padB, plotW, plotH, baseY, coords, line, area };
}

export default function WeeklyBarChart({ jsonPath = '/userdata.json' }) {
  const [weekly, setWeekly] = useState(null);
  const [hrDaily, setHrDaily] = useState(null);
  const [error, setError] = useState('');
  const [slide, setSlide] = useState(0);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setError('');
        // Commented for testing as approved by prof Ali
        // const { idToken } = useAuth()
        // const res = await fetch("http://localhost:8000/api/v1/users/dashboard", {
        //     method: "GET",
        //     headers: {
        //         "Authorization": `Bearer ${idToken}`,
        //         "Content-Type": "application/json",
        //     },
        // })

        // if (!res.ok) throw new Error("Failed to fetch dashboard")

        // return res.json()
        const res = await fetch(jsonPath, { cache: 'no-store' });
        if (!res.ok) throw new Error(`Failed to load: ${jsonPath}`);
        const json = await res.json();

        if (!cancelled) {
          setWeekly(json?.weekly_summary || null);
          setHrDaily(json?.heart_rate_daily || null);
        }
      } catch (e) {
        if (!cancelled) setError(e?.message || 'Failed to load chart data');
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [jsonPath]);

  //Weekly steps bar chart data
  const barData = useMemo(() => {
    const daily = weekly?.daily_steps || [];
    return daily.map((d) => ({
      day: dayLabel(d.date),
      value: toNum(d.steps, 0),
      date: d.date,
    }));
  }, [weekly]);

  const maxSteps = useMemo(() => {
    const vals = barData.map((d) => d.value);
    return Math.max(...vals, 1);
  }, [barData]);
  //Heart rate line chart data
  const hrPoints = useMemo(() => hrDaily?.points || [], [hrDaily]);
  const hrYMin = toNum(hrDaily?.y_min, 40);
  const hrYMax = toNum(hrDaily?.y_max, 120);

  const hrSvg = useMemo(() => {
    if (!hrPoints.length) return null;
    return buildHeartRatePaths(hrPoints, hrYMin, hrYMax);
  }, [hrPoints, hrYMin, hrYMax]);

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
  return (
    <div className="relative rounded-2xl border border-gray-200 bg-white shadow-[0_6px_0_rgba(0,0,0,0.06)] p-6">
      <button
        type="button"
        aria-label="Next"
        onClick={() => setSlide((s) => (s + 1) % 2)}
        className="absolute -right-4 top-1/2 -translate-y-1/2 h-9 w-9 rounded-full border border-gray-200 bg-white shadow flex items-center justify-center hover:bg-gray-50"
      >
        <span className="text-gray-700">›</span>
      </button>

      {slide === 0 ? (
        <>
          <div className="h-[420px] flex items-end gap-4 px-2 pt-6 pb-2">
            <div className="h-full w-12 flex flex-col justify-between text-[10px] text-gray-400">
              <span>{Math.round((maxSteps * 1.0) / 1000) * 1000}</span>
              <span>{Math.round((maxSteps * 0.75) / 1000) * 1000}</span>
              <span>{Math.round((maxSteps * 0.5) / 1000) * 1000}</span>
              <span>{Math.round((maxSteps * 0.25) / 1000) * 1000}</span>
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
                {barData.map((d) => {
                  const MAX_BAR_PX = 300;
                  const h = Math.max(3, (d.value / maxSteps) * MAX_BAR_PX);

                  return (
                    <div key={d.date} className="flex flex-col items-center gap-2 flex-1">
                      <div
                        className="w-full max-w-[54px] rounded-lg bg-blue-500"
                        style={{ height: `${h}px` }}
                        title={`${d.day}: ${d.value}`}
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
              <div className="text-sm text-gray-700 font-medium">{toNum(weekly.total_distance_km, 0)} km</div>
            </div>
            <div>
              <div className="text-[10px] text-gray-400">Active Days</div>
              <div className="text-sm text-gray-700 font-medium">{toNum(weekly.active_days, 0)}/7</div>
            </div>
          </div>
        </>
      ) :
        <>
          {!hrSvg ? (
            <div className="p-6 text-sm text-gray-500">No heart rate data found in heart_rate_daily.</div>
          ) : (
            <>
              <div className="w-full overflow-hidden rounded-2xl">
                <svg viewBox={`0 0 ${hrSvg.W} ${hrSvg.H}`} className="w-full h-[420px]">
                  {[0, 0.25, 0.5, 0.75, 1].map((t) => {
                    const y = hrSvg.padT + (1 - t) * hrSvg.plotH;
                    return (
                      <line key={t} x1={hrSvg.padL} x2={hrSvg.W - hrSvg.padR} y1={y} y2={y}
                        stroke="#e5e7eb" strokeDasharray="6 6" />
                    );
                  })}
                  {hrSvg.coords.map((c) => (
                    <line key={c.x} x1={c.x} x2={c.x} y1={hrSvg.padT} y2={hrSvg.baseY}
                      stroke="#e5e7eb" strokeDasharray="6 6" />
                  ))}

                  <path d={hrSvg.area} fill="rgba(255, 99, 99, 0.25)" />
                  <path d={hrSvg.line} fill="none" stroke="rgb(255, 99, 99)" strokeWidth="3" />
                  {[hrYMin, hrYMin + 20, hrYMin + 40, hrYMin + 60, hrYMax].map((val) => {
                    const y = hrSvg.padT + (1 - (val - hrYMin) / (hrYMax - hrYMin)) * hrSvg.plotH;
                    return (
                      <text key={val} x={hrSvg.padL - 10} y={y + 4} textAnchor="end" fontSize="16" fill="#6b7280">
                        {val}
                      </text>
                    );
                  })}

                  {hrSvg.coords.map((c) => (
                    <g key={c.x + 'dot'}>
                      <circle cx={c.x} cy={c.y} r="6" fill="rgb(255, 99, 99)" />
                      <circle cx={c.x} cy={c.y} r="3" fill="white" />
                      <text
                        key={c.x + c.label}
                        x={c.x}
                        y={hrSvg.baseY + 45}
                        textAnchor="middle"
                        fontSize="16"
                        fill="#6b7280"
                      >
                        {c.label}
                      </text>
                    </g>
                  ))}

                  {hrSvg.coords.map((c) => (
                    <g key={c.x + 'dot'}>
                      <circle cx={c.x} cy={c.y} r="6" fill="rgb(255, 99, 99)" />
                      <circle cx={c.x} cy={c.y} r="3" fill="white" />
                      <text x={c.x} y={c.y - 14} textAnchor="middle" fontSize="14"
                        fontWeight="500" fill="rgb(220, 60, 60)">
                        {c.bpm}
                      </text>
                    </g>
                  ))}
                </svg>
              </div>

              <div className="mt-2 grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-[10px] text-gray-400">Min BPM</div>
                  <div className="text-sm text-gray-700 font-medium">{hrYMin}</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">Avg Heart Rate</div>
                  <div className="text-sm text-gray-700 font-medium">
                    {Math.round(hrSvg.coords.reduce((sum, c) => sum + c.bpm, 0) / hrSvg.coords.length)} BPM
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">Max BPM</div>
                  <div className="text-sm text-gray-700 font-medium">{hrYMax}</div>
                </div>
              </div>
            </>
          )}
        </>
      }

      <div className="mt-5 flex items-center justify-center gap-2">
        <button
          type="button"
          aria-label="Show steps chart"
          onClick={() => setSlide(0)}
          className={`h-2 w-2 rounded-full ${slide === 0 ? 'bg-[#71E4FD]' : 'bg-gray-300'}`}
        />
        <button
          type="button"
          aria-label="Show heart rate chart"
          onClick={() => setSlide(1)}
          className={`h-2 w-2 rounded-full ${slide === 1 ? 'bg-[#71E4FD]' : 'bg-gray-300'}`}
        />
      </div>
    </div>
  );
}