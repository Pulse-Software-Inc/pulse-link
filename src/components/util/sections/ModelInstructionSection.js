"use client"

import { useState } from "react"
import { TextField } from "@mui/material"

/* ── User Profile ───────────────────────────────────── */
export default function UserProfileSection(props) {

  const formData = props.formData
  const updateField = props.updateField

  return (
    <section id="ai" className="scroll-mt-8">
      <h2 className="mb-5 text-xl font-bold" style={{ color: "#1a1a1a" }}>Customize Your AI Powered Mascot! (Experimental)</h2>
        <TextField
            label="Custom Instructions"
            InputLabelProps={{ shrink: true }}
            defaultValue={formData.fname}
            onBlur={(e) => updateField('ai_instructions', e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
    </section>
  )
}