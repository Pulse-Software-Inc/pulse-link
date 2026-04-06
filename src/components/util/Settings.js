"use client"

import proSettings from './data/proSettings.json'
import userSettings from './data/userSettings.json'
import { useState, useEffect, useCallback, useRef } from "react"
import { useSearchParams } from "next/navigation"
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
import { useRouter } from 'next/navigation';
import SettingsSidebar from "@/components/util/SettingsSidebar"
import UserProfileSection from "./sections/UserProfileSection"
import DataPrivacySection from "./sections/DataPrivacySection"
import GoalsSection from "./sections/GoalsSection"
import NotificationsSection from "./sections/NotificationsSection"
import InviteClientsSection from "./sections/InviteClientsSection"
import DevicesSection from "./sections/DevicesSection"


export default function Settings(props) {
  // finding ?role="" value
  const searchParams = useSearchParams()
  const role = searchParams.get("role")   // "user" | "professional"

  // states
  // const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState(() => {
    if (role === 'user') return userSettings
    if (role === 'professional') return proSettings
    return {}
  })
  const router = useRouter();

  // GET current settings from backend
  // useEffect(() => {
  //   async function fetchSettings() {
  //     try {
  //       const res = await fetch("http://localhost:8000/api/v1/users/settings/", {
  //         method: 'GET', headers: {
  //           'Authorization': `Bearer ${idToken}`,
  //           'Content-Type': 'application/json',
  //         }
  //       }); // your endpoint
  //       const data = await res.json()
  //       setCurrentSettings(data)
  //     } finally {
  //       setLoading(false)
  //     }
  //   }
  //   fetchSettings()
  // }, [])

  let sidebarLabels = [
    { id: "user-profile", label: "User Profile" },
    { id: "data-privacy", label: "Data and Privacy" },
  ]

  if (role == 'user') {
    sidebarLabels.push({ id: "goals", label: "Goals" },
      { id: "notifications", label: "Notifications" }, { id: "devices", label: "Devices" })
  } else if (role == 'professional') {
    sidebarLabels.push({ id: "invite-clients", label: "Invite Clients" })
  } else
    router.push('/util/settings?role=user');

  console.log(formData)
  // Handlers
  // In Settings.js, pass down to sections:
  const updateField = (key, value) =>
    setFormData(prev => ({ ...prev, [key]: value }))

  //OLD CODE
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
        navigation={{ activeSection, handleNavigate }}
        sidebarLabels={sidebarLabels}
      />

      <div className="relative flex flex-1 flex-col" style={{ background: "#ffffff" }}>
        <div className="absolute right-5 top-5 z-10">
          <IconButton
            onClick={() => router.back()}
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
        <div ref={scrollRef} className="settings-scroll flex-1 overflow-y-auto mx-auto max-w-2xl px-10 py-10">
          <div className="flex flex-col gap-10">
            <UserProfileSection formData={formData} updateField={updateField} />
            <hr style={{ borderColor: "#e5e7eb" }} />
            <DataPrivacySection />
            <hr style={{ borderColor: "#e5e7eb" }} />
            <DevicesSection />
            <hr style={{ borderColor: "#e5e7eb" }} />
            <NotificationsSection formData={formData} updateField={updateField} />
            <hr style={{ borderColor: "#e5e7eb" }} />
          </div>
        </div>
      </div>
    </main >
  )
}