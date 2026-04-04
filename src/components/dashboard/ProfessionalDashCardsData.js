'use client';

// Data for doctor dashboard cards (Total Clients, Active Alerts, Synced Today)

import { useEffect, useState } from 'react';

export default function useDoctorDB_cardsData(jsonPath = '/prodata.json') {
    const [cards, setCards] = useState([]);
    const [clients, setClients] = useState([]);
    const [providerName, setProviderName] = useState('');
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

                const provider = json?.provider_profile || {};
                const doctor = provider.name || json?.provider_name || 'Doctor';

                const rawClients = json?.clients || json?.patients || [];
                const clientsList = rawClients.map((p) => {
                    const displayName = p.name || p.fullName || p.displayName || p.email || p.uid || 'Unknown';
                    const lastSync = p.lastSync || p.last_activity || null;
                    const status = p.status || (p.consent_granted ? 'ACTIVE' : 'INACTIVE');

                    return {
                        id: p.id || p.uid || p.email,
                        name: displayName,
                        age: p.age ?? 'N/A',
                        lastSync,
                        lastSyncDisplay: lastSync ? new Date(lastSync).toLocaleDateString() : 'N/A',
                        status,
                        alerts: p.alerts || 0,
                    };
                });
                const activeClients = clientsList.filter(c => c.status === 'ACTIVE').length;
                const totalClients = clientsList.length;

                // Calculate synced today
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const syncedToday = clientsList.filter(c => {
                    if (!c.lastSync) return false;
                    const syncDate = new Date(c.lastSync);
                    syncDate.setHours(0, 0, 0, 0);
                    return syncDate.getTime() === today.getTime();
                }).length;

                // Count active alerts
                const activeAlerts = clientsList.reduce((sum, c) => sum + (c.alerts || 0), 0);

                const mapped = [
                    {
                        id: 'TotalClients',
                        title: 'Total Clients',
                        iconSrc: '/DashboardIcons/TotalClient_Icon.svg',
                        main: totalClients,
                        sub: ` ${activeClients} active`,
                    },
                    {
                        id: 'ActiveAlerts',
                        title: 'Active Alerts',
                        iconSrc: '/DashboardIcons/ActiveAlerts_Icon.svg',
                        main: activeAlerts,
                        sub: null,
                    },
                    {
                        id: 'SyncedToday',
                        title: 'Synced Today',
                        iconSrc: '/DashboardIcons/Synced_Icon.svg',
                        main: `${syncedToday}/${totalClients}`,
                        sub: null,
                    },
                ];

                    setProviderName(doctor);
                if (!cancelled) {
                    setCards(mapped);
                    setClients(clientsList);
                }
            } catch (e) {
                if (!cancelled) setError(e?.message || 'Unable to load dashboard');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();

        return () => { cancelled = true; };
    }, [jsonPath]);
    return { cards, clients, providerName, loading, error };
}
