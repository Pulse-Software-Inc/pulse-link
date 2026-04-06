"use client"

import { useState } from "react"
import {
  Switch,
  FormControlLabel,
} from "@mui/material"

export default function NotificationsSection(props) {
  const formData = props.formData
  const updateField = props.updateField


  return (
    <section id="notifications" className="scroll-mt-6">
      <h2 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}>Notifications</h2>
      <FormControlLabel
        control={
          <Switch
            checked={notifs}
            onChange={() => setNotifs(!notifs)}
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
          <span className="text-sm" style={{ color: "#1a1a1a" }}>
            Turn on notifications from PulseLink
          </span>
        }
      />
    </section>
  )
}