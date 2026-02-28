'use client';

//using this file for the data going to be used in the DB cards.

import { useEffect, useState } from 'react';

const num= (x,y=0) => (Number.isFinite(Number(x)) ? Number(x) : y);

const latestTime = (arr = []) => 
    Array.isArray(arr) && arr.length ? arr.reduce((best, cur) => 
        new Date(cur?.timestamp).getTime() > new Date(best?.timestamp).getTime() ? cur : best) : null;

export default function useDB_cardsData(
    jsonPath = '/userdata.json',
    stepGoal = 10000,
    kcalGoal = 2550) {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                setLoading(true);
                setError('');
                const res = await fetch(jsonPath, { cache: 'no-store' });
                if (!res.ok) throw new Error(`Failed to load: ${jsonPath}`);
                const json = await res.json();

                const s = json?.summary || {};
                const latest = latestTime(json?.biomarkers);
                const lastSync = json?.devices?.[0]?.last_sync || latest?.timestamp || null;
                const syncTxt = lastSync ? `Last sync: ${new Date(lastSync).toLocaleString()}` : null;
                const totalSteps = num(s.total_steps);
                const totalKcal = num(s.total_calories);
                const avgHr = num(s.avg_heart_rate);

                const mapped = [
                    {
                        id: 'Steps',
                        title: 'Steps',
                        iconSrc: '/Steps_Icon.svg',
                        main: totalSteps,
                        sub: `/${stepGoal}`,
                        footer: s.data_points ? `Data points: ${s.data_points}` : null,
                        progress: { value: totalSteps, max: num(stepGoal, 1) },
                    },
                    {
                        id: 'Kcal',
                        title: 'Calories Burned',
                        iconSrc: '/Calories_Icon.svg',
                        main: totalKcal,
                        sub: `/${kcalGoal}`,
                        footer: syncTxt,
                        progress: { value: totalKcal, max: num(kcalGoal, 1) },
                    },
                    {
                        id: 'Heart',
                        title: 'Heart Rate',
                        iconSrc: '/HeartRate_Icon.svg',
                        main: avgHr,
                        sub: 'BPM',
                        footer: syncTxt
                    },
                ];
                if (!cancelled) setCards(mapped);
            } catch (e) {
                if (!cancelled) setError(e?.message || 'Unable to load dashboard');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        
        return () => { cancelled = true; };
    }, [jsonPath, stepGoal, kcalGoal]);

    return {cards, loading, error};
} 