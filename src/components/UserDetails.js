'use client';

// Component to display selected client health details in the doctor dashboard.
import React, { useMemo } from 'react';
import DashCard from './dashboard/DashCards';
import WeeklyBarChart from './WeeklyBarChart';

const STEP_GOAL = 10000;
const CALORIE_GOAL = 500;
const KM_PER_STEP = 0.00075;

function toNum(value, fallback = 0) {
	if (typeof value === 'string') {
		value = value.replace(/,/g, '').trim();
	}
	const n = Number(value);
	return Number.isFinite(n) ? n : fallback;
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

	if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
		return value;
	}

	const date = new Date(value);
	if (Number.isNaN(date.getTime())) {
		return null;
	}

	return formatIsoDate(date);
}

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

function getHeartStatusLabel(value) {
	if (value <= 0) return 'UNKNOWN';
	if (value < 60) return 'LOW';
	if (value <= 100) return 'NORMAL';
	return 'HIGH';
}

function buildHeartRateDailyFromClient(biomarkers, weeklySummary) {
	const week = weeklySummary?.daily_steps || [];
	if (!week.length) {
		return null;
	}

	const ratesByDate = biomarkers.reduce((acc, point) => {
		const date = toIsoDate(point?.timestamp);
		const heartRate = toNum(point?.heart_rate, -1);
		if (!date || heartRate <= 0) {
			return acc;
		}

		const existing = acc.get(date) || [];
		existing.push(heartRate);
		acc.set(date, existing);
		return acc;
	}, new Map());

	const averages = week.map((day) => {
		const dayRates = ratesByDate.get(day.date) || [];
		if (!dayRates.length) {
			return 0;
		}

		const total = dayRates.reduce((sum, value) => sum + value, 0);
		return Math.round(total / dayRates.length);
	});

	const validRates = averages.filter((value) => value > 0);
	if (!validRates.length) {
		return null;
	}

	const yMin = Math.max(30, Math.min(...validRates) - 10);
	const yMax = Math.max(yMin + 20, Math.max(...validRates) + 10);

	const points = week.map((day, index) => ({
		label: dayLabel(day.date),
		bpm: averages[index] > 0 ? averages[index] : yMin,
	}));

	return {
		points,
		y_min: yMin,
		y_max: yMax,
	};
}

function buildChartDataPath(weeklySummary, heartRateDaily) {
	const payload = {
		weekly_summary: weeklySummary,
		heart_rate_daily: heartRateDaily || { points: [] },
	};

	return `data:application/json,${encodeURIComponent(JSON.stringify(payload))}`;
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
		const heartRateDaily = buildHeartRateDailyFromClient(biomarkers, weeklySummary);

		return {
			steps,
			calories,
			heartRate,
			restingHeartRate,
			heartStatus: getHeartStatusLabel(heartRate),
			weeklySummary,
			heartRateDaily,
		};
	}, [client]);

	const cards = useMemo(() => {
		if (!details) {
			return [];
		}

		return [
			{
				id: 'steps',
				iconSrc: '/DashboardIcons/Steps_Icon.svg',
				title: 'Steps',
				main: details.steps.toLocaleString(),
				sub: ` / ${STEP_GOAL.toLocaleString()}`,
				progress: { value: details.steps, max: STEP_GOAL },
				footer: '4% more than yesterday',
			},
			{
				id: 'calories',
				iconSrc: '/DashboardIcons/Calories_Icon.svg',
				title: 'Calories',
				main: details.calories.toLocaleString(),
				sub: ` / ${CALORIE_GOAL.toLocaleString()}`,
				progress: { value: details.calories, max: CALORIE_GOAL },
				footer: 'Daily calorie target',
			},
			{
				id: 'heart-rate',
				iconSrc: '/DashboardIcons/HeartRate_Icon.svg',
				title: 'Heart Rate',
				main: details.heartRate > 0 ? details.heartRate.toLocaleString() : 'N/A',
				sub: details.heartRate > 0 ? ' BPM' : '',
				footer: `Status: ${details.heartStatus} | Resting: ${details.restingHeartRate > 0 ? details.restingHeartRate : 'N/A'} BPM`,
			},
		];
	}, [details]);

	const chartDataPath = useMemo(() => {
		if (!details?.weeklySummary) {
			return '/userdata.json';
		}

		return buildChartDataPath(details.weeklySummary, details.heartRateDaily);
	}, [details]);

	if (!client || !details) {
		return null;
	}

	const closeButtonStyling = 'inline-flex h-8 w-8 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-100';

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/25 p-4">
			<div className="max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-3xl border border-gray-300 bg-[#f5f5f5] p-5 shadow-xl sm:p-6">
				<div className="flex items-start justify-between gap-4">
					<div>
						<h3 className="text-2xl font-normal text-gray-800">Client Details</h3>
						<p className="mt-1 text-sm text-gray-500">
							{client.name} | Age {client.age ?? 'N/A'} | Select a client to view their detailed health metrics
						</p>
					</div>
					<button
						type="button"
						onClick={onClose}
						aria-label="Close client details"
						className={closeButtonStyling}
					>
						X
					</button>
				</div>

				<div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
					{cards.map((val) => (
						<DashCard key={val.id} val={val} />
					))}
				</div>

				<div className="mt-4">
					<div className="compactChart mx-auto w-full max-w-4xl max-h-[400px]">
						<WeeklyBarChart jsonPath={chartDataPath} />
					</div>
				</div>
			</div>
		</div>
	);
}