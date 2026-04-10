"use server"

import { Resend } from "resend"

export async function sendInviteEmail(email, message) {
  const resend = new Resend(process.env.RESEND_API_KEY)
  await resend.emails.send({
    from: "PulseLink <onboarding@resend.dev>",
    to: email,
    subject: "You've been invited to PulseLink",
    html: `<p>${message}</p>`,
  })
}