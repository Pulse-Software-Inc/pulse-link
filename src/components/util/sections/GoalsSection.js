"use client"

import { TextField } from "@mui/material"
import Image from "next/image"


export default function NotificationsSection(props) {
  const GOAL_FIELDS = [
    { key: "steps", label: "Daily Steps", unit: "steps", icon: "/DashboardIcons/Steps_Icon.svg" },
    { key: "calories", label: "Calories Burned", unit: "kcal", icon: "/DashboardIcons/Calories_Icon.svg" },
    { key: "heart_rate", label: "Target Heart Rate", unit: "bpm", icon: "/DashboardIcons/HeartRate_Icon.svg" },
  ]
  const formData = props.formData
  const updateField = props.updateField

  const goals = formData.daily_goals
  const updateGoal = (key, value) =>
    updateField("daily_goals", { ...goals, [key]: Number(value) }) //Number so it's not saved as "9000" or "2200"

  return (
    <section id="goals" className="scroll-mt-8">
      <h2 className="mb-4 text-lg font-bold" style={{ color: "#1a1a1a" }}>Goals</h2>
      <div className="flex flex-col gap-3">
        {GOAL_FIELDS.map(({ key, label, unit, icon }) => (
          <div key={key} className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
            <div className="flex items-center gap-3">
              <Image src={icon} alt={label} width={24} height={24} />
              <span className="text-sm font-medium text-gray-900">{label}</span>
            </div>
            <div className="flex items-center gap-2">
              <TextField
                defaultValue={goals[key]}
                onBlur={(e) => updateGoal(key, e.target.value)}
                size="small"
                type="number"
                slotProps={{
                  input: {
                    sx: { fontSize: 14, color: "#1a1a1a", width: "100px" },
                    inputProps: { min: 0 }
                  },
                }}
              />
              <span className="text-xs text-gray-400 w-16">{unit}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}