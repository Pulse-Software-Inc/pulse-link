"use client"

import { useState } from "react"
import { TextField, Button } from "@mui/material"
import { sendInviteEmail } from "@/lib/sendInvite"


const STATUS_STYLES = {
  pending: { bg: "bg-yellow-100", text: "text-yellow-700", label: "pending..." },
  accepted: { bg: "bg-green-100", text: "text-green-700", label: "Accepted" },
  declined: { bg: "bg-red-100", text: "text-red-700", label: "Declined" },
}

export default function InviteClientsSection({ formData, updateField }) {
  if (!formData.invite_clients) return null

  const [newEmail, setNewEmail] = useState("")
  const [newMessage, setNewMessage] = useState("")
  const [emailError, setEmailError] = useState("")
  const [sending,    setSending]    = useState(false)
  const [sendError,  setSendError]  = useState("")

  const invites = formData.invite_clients

  const handleInvite = async () => {
    if (!newEmail.includes("@")) {
      setEmailError("Enter a valid email address.")
      return
    }
    if (invites.some(i => i.email === newEmail)) {
      setEmailError("This client has already been invited.")
      return
    }

    setSending(true)
    setSendError("")
    try {
      console.log("Sending Email....")
      await sendInviteEmail(newEmail, newMessage || "Join PulseLink")
      console.log("Sent!")
      updateField("invite_clients", [
        ...invites,
        { email: newEmail, message: newMessage || "Join PulseLink", status: "pending" }
      ])
      setNewEmail("")
      setNewMessage("")
      setEmailError("")
    } catch {
      setSendError("Failed to send invite. Please try again.")
    } finally {
      setSending(false)
    }
  }

  const removeInvite = (email) =>
    // Backend will automatically adjust by removing client from 'invited' list & making the invite sent useless
    updateField("invite_clients", invites.filter(i => i.email !== email))


  return (
    <section id="invite-clients" className="scroll-mt-8">
      <h2 className="mb-4 text-lg font-bold" style={{ color: "#1a1a1a" }}>Invite Clients</h2>


      <div className="flex flex-col gap-3">
        <TextField
          label="Client Email"
          InputLabelProps={{ shrink: true }}
          value={newEmail}
          onChange={(e) => { setNewEmail(e.target.value); setEmailError("") }}
          error={!!emailError}
          helperText={emailError}
          size="small"
          fullWidth
          slotProps={{ input: { sx: { fontSize: 14, color: "#1a1a1a" } } }}
        />
        <TextField
          label="Message (optional)"
          InputLabelProps={{ shrink: true }}
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Join PulseLink"
          size="small"
          fullWidth
          slotProps={{ input: { sx: { fontSize: 14, color: "#1a1a1a" } } }}
        />
        <div className="flex justify-end mb-4">
          <Button
            type="button"
            variant="contained"
            onClick={handleInvite}
            sx={{
              textTransform: "none",
              background: "linear-gradient(to right, #B2C4FE, #ECB6E6)",
              fontWeight: 600,
              fontSize: 12,
              borderRadius: "20px",
              boxShadow: "none",
              "&:hover": { opacity: 0.9, boxShadow: "none" },
            }}
          >
            Send Invite
          </Button>
        </div>
      </div>

      {/* Existing invites */}
      {invites.length === 0 ? (
        <p className="text-sm text-gray-400">No clients invited yet.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {invites.map((invite) => {
            const style = STATUS_STYLES[invite.status] ?? STATUS_STYLES.pending
            return (
              <div key={invite.email} className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
                <div>
                  <p className="text-sm font-medium text-gray-900">{invite.email}</p>
                  <p className="text-xs text-gray-400">{invite.message}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-md text-xs font-semibold ${style.bg} ${style.text}`}>
                    {style.label}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeInvite(invite.email)}
                    className="text-xs text-gray-400 hover:text-red-500 transition-colors"
                  >
                    REMOVE
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}