"use client"

import { Avatar } from "@mui/material"
import Image from "next/image"

const generalLinks = [
  { id: "user-profile", label: "User Profile" },
  { id: "authorized-access", label: "Authorized Access" },
  { id: "data-privacy", label: "Data and Privacy" },
  { id: "appearance", label: "Appearance" },
]

const personalLinks = [
  { id: "goals", label: "Goals" },
  { id: "notifications", label: "Notifications" },
]

export function SettingsSidebar({ activeSection, onNavigate }) {
  return (
    <aside
      className="flex h-full w-[260px] shrink-0 flex-col justify-between px-6 py-8"
      style={{
        background:
          "linear-gradient(135deg, #5EEDFD 0%, #DDB1FC 50%, #FFBBC9 100%)",
      }}
    >
      <div>
        <div className="mb-8 flex items-center gap-3">
          <Avatar
            sx={{
              width: 44,
              height: 44,
              bgcolor: "rgba(255,255,255,0.25)",
              color: "#fff",
              fontSize: 18,
              fontWeight: 600,
            }}
          >
            U
          </Avatar>
          <span className="text-sm font-semibold text-white">User 1</span>
        </div>

        <div className="mb-6">
          <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/50">
            General Settings
          </p>
          <nav className="flex flex-col gap-0.5">
            {generalLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => onNavigate(link.id)}
                className={`rounded-md px-3 py-2 text-left text-[13px] font-medium transition-colors ${
                  activeSection === link.id
                    ? "bg-white/25 text-white"
                    : "text-white/75 hover:bg-white/10 hover:text-white"
                }`}
              >
                {link.label}
              </button>
            ))}
          </nav>
        </div>

        <div>
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-white/50">
            Personal Settings
          </p>
          <nav className="flex flex-col gap-0.5">
            {personalLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => onNavigate(link.id)}
                className={`rounded-md px-3 py-2 text-left text-[13px] font-medium transition-colors ${
                  activeSection === link.id
                    ? "bg-white/25 text-white"
                    : "text-white/75 hover:bg-white/10 hover:text-white"
                }`}
              >
                {link.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <button className="flex items-center gap-2 rounded-md px-3 py-2 text-left text-[13px] font-medium text-white/75 transition-colors hover:bg-white/10 hover:text-white">
        <Image src="/LogOut_Icon.svg" alt="Log Out" width={20} height={20} />
        Log Out
      </button>
    </aside>
  )
}
