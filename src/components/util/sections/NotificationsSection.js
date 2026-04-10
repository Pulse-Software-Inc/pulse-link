"use client"

import { useState } from "react"
import {
  Switch,
  FormControlLabel,
} from "@mui/material"

function ToggleRow({ label, checked, onChange }) {
  return (
    <FormControlLabel
      control={
        <Switch
          checked={checked}
          onChange={onChange}
          size="small"
          sx={{
            "& .MuiSwitch-switchBase.Mui-checked": { color: "#e1b3f6" },
            "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
              backgroundColor: "#e1b3f6",
            },
          }}
        />
      }
      label={
        <span className="text-sm" style={{ color: "#1a1a1a" }}>{label}</span>
      }
    />
  )
}

export default function NotificationsSection(props) {
  const formData = props.formData
  const updateField = props.updateField
  const prefs = formData.notification_preferences
  const toggle = (key) =>
    updateField("notification_preferences", { ...prefs, [key]: !prefs[key] })
  const notificationToggles = [
    { key: "mute_all", label: "Turn off notifications from PulseLink" },
    { key: "general", label: "Email me about general metric changes" },
    { key: "appointment", label: "Send alerts for professional booked appointments" },
    { key: "provider_alert", label: "Recieve pings from provider" },
    { key: "emergency", label: "Recieve notification when metrics are irregular" },
    { key: "companion", label: "Receive updates from companion" },
    { key: "daily_summary", label: "Recieve Daily Summaries" },
  ]

  return (
    <section id="notifications" className="scroll-mt-6">
      <h2 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}>
        Notifications
      </h2>
      <div className="flex flex-col gap-2">
        {notificationToggles.map(({ key, label }) => (
          <ToggleRow
            key={key}
            label={label}
            checked={prefs[key] ?? false}
            onChange={() => toggle(key)}
          />
        ))}
      </div>
    </section>
  )
}