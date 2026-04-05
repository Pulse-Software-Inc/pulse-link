'use client';

// Component to display detailed health metrics and weekly summary charts for a selected client in the doctor dashboard.
import React, { useMemo } from 'react';
import Image from 'next/image';

const STEP_GOAL = 10000;
const CALORIE_GOAL = 500;
const KM_PER_STEP = 0.00075;

// this function makes sure value is within the range
function clamp(value, min, max) {
	return Math.max(min, Math.min(max, value));
}

function toNum(value, fallback = 0) {
	if (typeof value === 'string') {
		value = value.replace(/,/g, '').trim(); // Remove commas and trim whitespace
	}
	const n = Number(value);
	return Number.isFinite(n) ? n : fallback;// Return fallback if value is not a finite number
}

function dayLabel(dateStr) {
	const d = new Date(`${dateStr}T00:00:00`);
	if (Number.isNaN(d.getTime())) return 'Day';
	return d.toLocaleDateString('en-US', { weekday: 'short' });
}

function formatIsoDate(date) {
	return date.toISOString().slice(0, 10);
}


function toIsoDate(value) {
	if (!value) {
		return null;
	}
// If the value is already a string in YYYY-MM-DD format, return it as is
	if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
		return value;
	}

	const date = new Date(value);
	if (Number.isNaN(date.getTime())) {
		return null;
	}

	return formatIsoDate(date);
}

// the main part of the component that builds the weekly summary from client data, including steps, calories, heart rate, and generates the weekly bar chart data. 
// It also determines the heart rate status and formats the data for display in the metric cards and charts.
function buildWeeklySummaryFromClient(client, summary, biomarkers) {
	const existingWeekly = client?.weeklySummary;
	if (Array.isArray(existingWeekly?.daily_steps) && existingWeekly.daily_steps.length > 0) {
		const dailySteps = existingWeekly.daily_steps
			.slice(-7)
			.map((entry) => ({
				date: toIsoDate(entry?.date),
				steps: Math.max(0, Math.round(toNum(entry?.steps, 0))),
			}))
			.filter((entry) => Boolean(entry.date));

		const totalSteps = dailySteps.reduce((sum, day) => sum + day.steps, 0);
		return {
			daily_steps: dailySteps,
			average_steps: toNum(existingWeekly.average_steps, Math.round(totalSteps / Math.max(dailySteps.length, 1))),
			total_distance_km: toNum(existingWeekly.total_distance_km, Number((totalSteps * KM_PER_STEP).toFixed(1))),
			active_days: toNum(existingWeekly.active_days, dailySteps.filter((day) => day.steps > 0).length),
		};
	}

	const stepsByDate = biomarkers.reduce((acc, point) => {
		const date = toIsoDate(point?.timestamp);
		const steps = toNum(point?.steps, -1);
		if (!date || steps < 0) {
			return acc;
		}

		const previous = acc.get(date);
		acc.set(date, previous == null ? steps : Math.max(previous, steps));
		return acc;
	}, new Map());

	let anchorDate = null;
	if (stepsByDate.size > 0) {
		const latestKnownDate = [...stepsByDate.keys()].sort().at(-1);
		anchorDate = new Date(`${latestKnownDate}T00:00:00`);
	}

	if (!anchorDate || Number.isNaN(anchorDate.getTime())) {
		anchorDate = new Date(client?.lastSync || Date.now());
	}

	if (Number.isNaN(anchorDate.getTime())) {
		anchorDate = new Date();
	}

	anchorDate.setHours(0, 0, 0, 0);

	const daily_steps = [];
	for (let i = 6; i >= 0; i -= 1) {
		const d = new Date(anchorDate);
		d.setDate(anchorDate.getDate() - i);
		const date = formatIsoDate(d);
		daily_steps.push({
			date,
			steps: Math.max(0, Math.round(toNum(stepsByDate.get(date), 0))),
		});
	}

	// If no steps were recorded for the week but we have a weekly total then we will distribute it evenly across the days
	const hasMeasuredSteps = daily_steps.some((day) => day.steps > 0);
	if (!hasMeasuredSteps) {
		const weeklyTotal = Math.round(toNum(summary?.total_steps, 0));
		if (weeklyTotal > 0) {
			const baseSteps = Math.floor(weeklyTotal / 7);
			let remainder = weeklyTotal - baseSteps * 7;
			daily_steps.forEach((day) => {
				day.steps = baseSteps + (remainder > 0 ? 1 : 0);
				remainder -= remainder > 0 ? 1 : 0;
			});
		}
	}

	const totalSteps = daily_steps.reduce((sum, day) => sum + day.steps, 0);
	return {
		daily_steps,
		average_steps: Math.round(totalSteps / Math.max(daily_steps.length, 1)),
		total_distance_km: Number((totalSteps * KM_PER_STEP).toFixed(1)),
		active_days: daily_steps.filter((day) => day.steps > 0).length,
	};
}

function getHeartStatus(value) {
	if (value <= 0) {
		return {
			label: 'UNKNOWN',
			className: 'bg-gray-200 text-gray-700',
		};
	}

	if (value < 60) {
		return {
			label: 'LOW',
			className: 'bg-amber-100 text-amber-700',
		};
	}

	if (value <= 100) {
		return {
			label: 'NORMAL',
			className: 'bg-green-100 text-green-700',
		};
	}

	return {
		label: 'HIGH',
		className: 'bg-red-100 text-red-700',
	};
}

function ProgressBar({ value = 0, max = 100 }) {
	const safeMax = max === 0 ? 1 : max;
	const width = clamp((value / safeMax) * 100, 0, 100);

	return (
		<div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
			<div className="h-full rounded-full bg-gray-500" style={{ width: `${width}%` }} />
		</div>
	);
}

function MetricCard({ iconSrc, title, mainText, subText, progress, footer, statusBadge }) {
	return (
		<article className="rounded-2xl border border-gray-300 bg-white p-4 shadow-[0_3px_6px_rgba(0,0,0,0.08)]">
			<div className="flex items-center gap-2">
				<Image src={iconSrc} alt={`${title} icon`} width={16} height={16} className="h-4 w-4" />
				<h4 className="text-base font-semibold text-gray-900">{title}</h4>
			</div>

			<div className="mt-3 text-gray-900">
				<span className="text-2xl font-bold">{mainText}</span>
				{subText ? <span className="ml-1 text-sm text-gray-500">{subText}</span> : null}
			</div>

			{progress ? (
				<div className="mt-3">
					<ProgressBar value={progress.value} max={progress.max} />
				</div>
			) : null}

			{statusBadge ? (
				<div className="mt-2">
					<span className={`inline-flex rounded px-2 py-1 text-[10px] font-semibold ${statusBadge.className}`}>
						{statusBadge.label}
					</span>
				</div>
			) : null}

			{footer ? <p className="mt-2 text-xs text-gray-500">{footer}</p> : null}
		</article>
	);
}

function ClientWeeklyBarChart({ weeklySummary }) {
	const chartData = useMemo(() => {
		const daily = weeklySummary?.daily_steps || [];
		return daily.map((d) => ({
			day: dayLabel(d.date),
			value: toNum(d.steps, 0),
			date: d.date,
		}));
	}, [weeklySummary]);

	const maxVal = useMemo(() => {
		const vals = chartData.map((d) => d.value);
		return Math.max(...vals, 1);
	}, [chartData]);

	if (!weeklySummary?.daily_steps?.length) {
		return (
			<div className="rounded-2xl border border-gray-200 bg-white p-6 text-sm text-gray-500 shadow-[0_6px_0_rgba(0,0,0,0.06)]">
				No weekly step data available for this client.
			</div>
		);
	}

	return (
		<div className="relative rounded-2xl border border-gray-200 bg-white p-6 shadow-[0_6px_0_rgba(0,0,0,0.06)]">
			<button
				type="button"
				aria-label="Next"
				className="absolute -right-4 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full border border-gray-200 bg-white shadow hover:bg-gray-50"
			>
				<span className="text-gray-700">›</span>
			</button>
			<div className="flex h-[220px] items-end gap-4 px-2 pb-2 pt-6">
				<div className="flex h-full w-12 flex-col justify-between text-[10px] text-gray-400">
					<span>{Math.round((maxVal * 1.0) / 1000) * 1000}</span>
					<span>{Math.round((maxVal * 0.75) / 1000) * 1000}</span>
					<span>{Math.round((maxVal * 0.5) / 1000) * 1000}</span>
					<span>{Math.round((maxVal * 0.25) / 1000) * 1000}</span>
					<span>0</span>
				</div>
				<div className="relative h-full flex-1">
					<div className="pointer-events-none absolute inset-0">
						<div className="h-full w-full rounded-lg border border-dashed border-gray-100" />
						<div className="absolute left-0 right-0 top-1/4 border-t border-dashed border-gray-100" />
						<div className="absolute left-0 right-0 top-1/2 border-t border-dashed border-gray-100" />
						<div className="absolute left-0 right-0 top-3/4 border-t border-dashed border-gray-100" />
					</div>
					<div className="relative flex h-full items-end justify-between gap-4 px-3">
						{chartData.map((d) => {
							const MAX_BAR_PX = 160;
							const h = Math.max(3, (d.value / maxVal) * MAX_BAR_PX);
							return (
								<div key={d.date} className="flex flex-1 flex-col items-center gap-2">
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
					<div className="text-sm font-medium text-gray-700">
						{toNum(weeklySummary.average_steps, 0).toLocaleString()}
					</div>
				</div>
				<div>
					<div className="text-[10px] text-gray-400">Total Distance</div>
					<div className="text-sm font-medium text-gray-700">
						{toNum(weeklySummary.total_distance_km, 0)} km
					</div>
				</div>
				<div>
					<div className="text-[10px] text-gray-400">Active Days</div>
					<div className="text-sm font-medium text-gray-700">
						{toNum(weeklySummary.active_days, 0)}/7
					</div>
				</div>
			</div>
		</div>
	);
}

export default function UserGraphs({ client, onClose }) {
	const details = useMemo(() => {
		if (!client) {
			return null;
		}

		const summary = client.summary || {};
		const biomarkers = Array.isArray(client.recentBiomarkers) ? client.recentBiomarkers : [];

		const latestBiomarker = biomarkers.reduce((latest, current) => {
			if (!latest) {
				return current;
			}

			const latestTs = new Date(latest?.timestamp || 0).getTime();
			const currentTs = new Date(current?.timestamp || 0).getTime();
			return currentTs > latestTs ? current : latest;
		}, null);

		const fallbackSteps = toNum(summary.total_steps, 0) > 0 ? toNum(summary.total_steps, 0) / 7 : 0;
		const fallbackCalories = toNum(summary.total_calories, 0) > 0 ? toNum(summary.total_calories, 0) / 7 : 0;
		const steps = Math.round(toNum(latestBiomarker?.steps, fallbackSteps));
		const calories = Math.round(toNum(latestBiomarker?.calories, fallbackCalories));
		const heartRate = Math.round(toNum(latestBiomarker?.heart_rate, toNum(summary.avg_heart_rate, 0)));

		const heartRateSamples = biomarkers
			.map((point) => toNum(point?.heart_rate, -1))
			.filter((value) => value > 0);
		const restingHeartRate = heartRateSamples.length
			? Math.round(Math.min(...heartRateSamples))
			: Math.max(0, heartRate > 0 ? heartRate - 10 : 0);

		const weeklySummary = buildWeeklySummaryFromClient(client, summary, biomarkers);

		return {
			steps,
			calories,
			heartRate,
			restingHeartRate,
			heartStatus: getHeartStatus(heartRate),
			weeklySummary,
		};
	}, [client]);

	if (!client || !details) {
		return null;
	}

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/25 p-4">
			<div className="w-full max-w-5xl rounded-[28px] border border-gray-300 bg-[#f5f5f5] p-5 shadow-[0_16px_32px_rgba(0,0,0,0.18)] sm:p-6">
				<div className="flex items-start justify-between gap-4">
					<div>
						<h3 className="text-xl font-semibold text-gray-900">Client Details</h3>
						<p className="mt-1 text-sm text-gray-500">
							{client.name} | Age {client.age ?? 'N/A'} | Select a client to view their detailed health metrics
						</p>
					</div>
					<button
						type="button"
						onClick={onClose}
						aria-label="Close client details"
						className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#d8b9ff] bg-[#f2e8ff] text-[#b27be8] transition-colors hover:bg-[#ead8ff]"
					>
						X
					</button>
				</div>

				<div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
					<MetricCard
						iconSrc="/DashboardIcons/Steps_Icon.svg"
						title="Steps"
						mainText={details.steps.toLocaleString()}
						subText={`/ ${STEP_GOAL.toLocaleString()}`}
						progress={{ value: details.steps, max: STEP_GOAL }}
						footer="4% more than yesterday"
					/>

					<MetricCard
						iconSrc="/DashboardIcons/Calories_Icon.svg"
						title="Calories"
						mainText={details.calories.toLocaleString()}
						subText={`/ ${CALORIE_GOAL.toLocaleString()}`}
						progress={{ value: details.calories, max: CALORIE_GOAL }}
						footer="Daily calorie target"
					/>

					<MetricCard
						iconSrc="/DashboardIcons/HeartRate_Icon.svg"
						title="Heart Rate"
						mainText={details.heartRate > 0 ? details.heartRate.toLocaleString() : 'N/A'}
						subText={details.heartRate > 0 ? 'BPM' : ''}
						statusBadge={details.heartStatus}
						footer={`Resting: ${details.restingHeartRate > 0 ? details.restingHeartRate : 'N/A'} BPM`}
					/>
				</div>

				<div className="mt-4">
					<ClientWeeklyBarChart weeklySummary={details.weeklySummary} />
				</div>
			</div>
		</div>
	);
}
