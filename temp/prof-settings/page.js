"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import {
  IconButton,
  Button,
  Avatar,
  TextField,
  Chip,
  Switch,
  FormControlLabel,
} from "@mui/material"
import Image from "next/image"
import { SettingsSidebar } from "@/components/settings_dr_sidebar"

const sectionIds = [
  "user-profile",
  "data-privacy",
  "appearance",
  "notifications",
]
/* ── Data and Privacy ── */
function DataPrivacySection() {
  return (
    <section id="data-privacy" className="scroll-mt-8">
      <h2 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}>
        Data and Privacy
      </h2>
      <p className="mb-4 text-sm leading-relaxed" style={{ color: "#6b7280" }}>
        We need to store and process some data in order to offer you the basic
        PulseLink service, such as your health metrics, wearable device data,
        and shared information between you and your healthcare providers. By
        using PulseLink, you allow us to provide this essential functionality
        and enable real-time health tracking.
      </p>
      <p className="text-sm leading-relaxed" style={{ color: "#6b7280" }}>
        {"You can stop this by "}
        <a href="#" className="font-semibold underline" style={{ color: "#ef5350" }}>
          deleting your account
        </a>
        {" and "}
        <a href="#" className="font-semibold underline" style={{ color: "#1e88e5" }}>
          disconnecting your linked devices.
        </a>
      </p>
    </section>
  )
}
/* ── Appearance ──*/
function AppearanceSection() {
  const [darkMode, setDarkMode] = useState(false)

  const handleToggle = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark") // need to add 'dark' class on a root for Tailwind dark mode to work
  }

  return (
    <section id="appearance" className="scroll-mt-6">
      <h2 className="mb-3 text-lg font-bold text-foreground">Appearance</h2>
      <FormControlLabel
        control={
          <Switch
            checked={darkMode}
            onChange={handleToggle}
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
          <span className="text-sm text-foreground">Turn on dark mode</span>
        }
      />
    </section>
  )
}
/* ── Notifications ─── */
function NotificationsSection() {
  const [notifs, setNotifs] = useState(true)

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
export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("user-profile")
  const scrollRef = useRef(null)
  const isScrollingFromClick = useRef(false)

  const handleNavigate = useCallback((sectionId) => {
    setActiveSection(sectionId)
    isScrollingFromClick.current = true

    const el = document.getElementById(sectionId)
    if (el && scrollRef.current) {
      const container = scrollRef.current
      const elTop = el.offsetTop - container.offsetTop
      container.scrollTo({ top: elTop - 32, behavior: "smooth" })

      setTimeout(() => {
        isScrollingFromClick.current = false
      }, 800)
    }
  }, [])

  useEffect(() => {
    const container = scrollRef.current
    if (!container) return

    const handleScroll = () => {
      if (isScrollingFromClick.current) return

      const scrollTop = container.scrollTop + 80

      for (let i = sectionIds.length - 1; i >= 0; i--) {
        const el = document.getElementById(sectionIds[i])
        if (el) {
          const elTop = el.offsetTop - container.offsetTop
          if (scrollTop >= elTop) {
            setActiveSection(sectionIds[i])
            return
          }
        }
      }
      setActiveSection(sectionIds[0])
    }

    container.addEventListener("scroll", handleScroll, { passive: true })
    return () => container.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <main className="flex h-screen w-screen overflow-hidden" style={{ background: "#ffffff" }}>
      <SettingsSidebar
        activeSection={activeSection}
        onNavigate={handleNavigate}
      />

      <div className="relative flex flex-1 flex-col" style={{ background: "#ffffff" }}>
        <div className="absolute right-5 top-5 z-10">
          <IconButton
            size="small"
            sx={{
              color: "#ffffff",
              border: "1px solid #ffffff",
              bgcolor: "#fff",
              "&:hover": { bgcolor: "#f9fafb" },
            }}
          >
            <Image src="/CrossX_Icon.svg" alt="Close" width={24} height={24} />
          </IconButton>
        </div>

        <div
          ref={scrollRef}
          className="settings-scroll flex-1 overflow-y-auto"
        >
          <div className="mx-auto max-w-2xl px-10 py-10">
            <div className="flex flex-col gap-10">
              <UserProfileSection />
              <hr style={{ borderColor: "#e5e7eb" }} />
              <DataPrivacySection />
              <hr style={{ borderColor: "#e5e7eb" }} />
              <AppearanceSection />
              <hr style={{ borderColor: "#e5e7eb" }} />
              <NotificationsSection />
              <hr style={{ borderColor: "#e5e7eb" }} />

              <div className="pb-10">
                <Button
                  variant="contained"
                  sx={{
                    textTransform: "none",
                    bgcolor: "#FF6363",
                    fontWeight: 700,
                    fontSize: 12,
                    borderRadius: "6px",
                    px: 3,
                    "&:hover": { bgcolor: "#FF6363" },
                  }}
                >
                  DELETE ACCOUNT
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
