"use client"

import { useState } from "react"
import { TextField } from "@mui/material"

/* ── User Profile ───────────────────────────────────── */
export default function UserProfileSection(props) {

  const formData = props.formData
  const updateField = props.updateField
  const [emailError, setEmailError] = useState("")

  const handleEmailChange = (e) => {
    const value = e.target.value
    if (value && !value.includes("@")) {
      setEmailError("Email must contain @")
    } else {
      setEmailError("")
      updateField('email', value)
    }
  }

  return (
    <section id="user-profile" className="scroll-mt-8">
      <h2 className="mb-5 text-xl font-bold" style={{ color: "#1a1a1a" }}>User Profile</h2>

      <div className="rounded-xl p-6" style={{ border: "1px solid #d1d5db", background: "#fff" }}>

        <div className="mb-4 grid grid-cols-2 gap-4">
          <TextField
            label="First name"
            InputLabelProps={{ shrink: true }}
            defaultValue={formData.fname}
            onBlur={(e) => updateField('fname', e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
          <TextField
            label="Last name"
            InputLabelProps={{ shrink: true }}
            defaultValue={formData.lname}
            onBlur={(e) => updateField('lname', e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: { fontSize: 14, color: "#1a1a1a" }
              },
            }}
          />
        </div>

        <div className="mb-4 grid grid-cols-2 gap-4">
          <TextField
            label="Email"
            InputLabelProps={{ shrink: true }}
            defaultValue={formData.email}
            onBlur={handleEmailChange}
            error={!!emailError}
            helperText={emailError}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />

          <TextField
            label="Password"
            InputLabelProps={{ shrink: true }}
            defaultValue={formData.password}
            onBlur={(e) => updateField('password', e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
        </div>
      </div>
    </section>
  )
}