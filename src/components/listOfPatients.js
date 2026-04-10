'use client';
import React, { useState } from 'react';
import UserGraphs from './UserDetails.js';

function ListOfPatients({ loading, error, clients = [] }) {
	const [selectedClient, setSelectedClient] = useState(null);

	const formatLastSync = (client) => {
		if (!client?.lastSync) return client?.lastSyncDisplay || 'N/A';
		const syncDate = new Date(client.lastSync);
		if (Number.isNaN(syncDate.getTime())) return client?.lastSyncDisplay || 'N/A';

		const diffMs = Date.now() - syncDate.getTime();
		const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
		const diffDays = Math.floor(diffHours / 24);

		if (diffHours < 1) return 'Just now';
		if (diffHours < 24) return `${diffHours} h ago`;
		if (diffDays === 1) return '1 day ago';
		if (diffDays <= 7) return `${diffDays} days ago`;

		return client?.lastSyncDisplay || syncDate.toLocaleDateString();
	};

	return (
		<>
			<section className="rounded-2xl border border-gray-300 bg-white p-4 shadow-[0_2px_6px_rgba(0,0,0,0.08)] sm:p-6">
				<h2 className="text-xl font-medium text-gray-900 sm:text-2xl">Client Details</h2>
				<p className="mt-1 text-sm text-gray-500">Select a client to view their detailed health metrics</p>

				<div className="mt-4 rounded-xl border border-gray-300 bg-white p-2 sm:p-3">
					{loading ? (
						<div className="p-4 text-sm text-gray-500">Loading client data...</div>
					) : error ? (
						<div className="p-4 text-sm text-red-600">{error}</div>
					) : clients.length === 0 ? (
						<div className="p-4 text-sm text-gray-500">No clients found.</div>
					) : (
						<div className="space-y-2">
							{clients.map((client) => (
								<div
									key={client.id}
									className="flex flex-col gap-3 rounded-lg border border-gray-300 bg-white px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
								>
									<div className="flex min-w-0 items-center gap-3">
										<div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-500 text-[11px] font-semibold text-white">
											{/* the dashboard icon color cannot be changed */}
											<img src="/Sidebar/Dashboard_Icon.svg" alt="Dashboard Icon" className="h-4 w-4" />
										</div>
										<div className="min-w-0">
											<p className="truncate text-lg leading-tight text-gray-900 sm:text-xl">{client.name}</p>
											<p className="mt-1 truncate text-sm text-gray-500">
												Age {client.age ?? 'N/A'} - Last Sync {formatLastSync(client)}
											</p>
										</div>
									</div>

										<div className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:gap-3 sm:self-auto">
										<div className="hidden text-xs text-gray-600 sm:block">Status</div>
										<span
											className={`inline-flex items-center rounded-md px-2 py-1 text-[10px] font-bold tracking-wide ${
												client.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-700'
											}`}
										>
											{client.status || 'UNKNOWN'}
										</span>
										<button
											type="button"
											onClick={() => setSelectedClient(client)}
												className="inline-flex h-9 w-full items-center justify-center rounded-lg border border-gray-300 bg-white px-4 text-xs font-semibold text-gray-900 shadow-sm transition-colors hover:bg-gray-100 sm:w-auto"
										>
											VIEW DETAILS
										</button>
									</div>
								</div>
							))}
						</div>
					)}
				</div>
			</section>

			<UserGraphs client={selectedClient} onClose={() => setSelectedClient(null)} />
		</>
	);
}

export default ListOfPatients;
