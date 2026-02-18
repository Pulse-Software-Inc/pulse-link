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
import { SettingsSidebar } from "@/components/settings_user_sidebar"

const sectionIds = [
  "user-profile",
  "authorized-access",
  "data-privacy",
  "appearance",
  "goals",
  "notifications",
]

/* ── User Profile ───────────────────────────────────── */
function UserProfileSection() {
    const [editing, setEditing] = useState(false)
  const [firstName, setFirstName] = useState("First Name")
  const [lastName, setLastName] = useState("Last Name")
  const [email, setEmail] = useState("**********@email.com")
  const [phone, setPhone] = useState("*********1234")
  const [emailError, setEmailError] = useState("")
  const [phoneError, setPhoneError] = useState("")

  const handleEmailChange = (e) => {
    const value = e.target.value
    setEmail(value)
    if (value && !value.includes("@")) {
      setEmailError("Email must contain @")
  }   else {
      setEmailError("")
    }
  }
  const handlePhoneChange = (e) => {
    const value = e.target.value
    const numbersOnly = value.replace(/[^0-9*+\-() ]/g, "")
    setPhone(numbersOnly)
    if (value !== numbersOnly) {
      setPhoneError("Only numbers are allowed")
    } else {
      setPhoneError("")
    }
  }

  const handleSave = () => {
    if (editing) {
      if (!email.includes("@")) {
        setEmailError("Email must contain @")
        return
      }
      if (phone && !/^[0-9*+\-() ]*$/.test(phone)) {
        setPhoneError("Only numbers are allowed")
        return
      }
    }
    setEditing(!editing)
  }
  return (
    <section id="user-profile" className="scroll-mt-8">
      <h2 className="mb-5 text-xl font-bold" style={{ color: "#1a1a1a" }}>User Profile</h2>

      <div className="rounded-xl p-6" style={{ border: "1px solid #d1d5db", background: "#fff" }}>
        <div className="mb-6 flex items-center gap-4">
          <Avatar
            sx={{
              width: 60,
              height: 60,
              bgcolor: "#f3f4f6",
              color: "#9ca3af)",
              fontSize: 22,
              fontWeight: 600,
            }}
          >
            U
          </Avatar>
          <Button
            variant="outlined"
            size="small"
            sx={{
              textTransform: "none",
              borderColor: "#d1d5db",
              color: "#6b7280",
              fontSize: 13,
              borderRadius: "8px",
              "&:hover": {
                borderColor: "#9ca3af",
                bgcolor: "#f9fafb",
              },
            }}
          >
            Edit profile picture
          </Button>
        </div>

        <div className="mb-4 grid grid-cols-2 gap-4">
          <TextField
            label="First name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                readOnly: !editing,
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
          <TextField
            label="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                readOnly: !editing,
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
        </div>

        <div className="mb-4 grid grid-cols-2 gap-4">
          <TextField
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={!!emailError}
            helperText={emailError}
            size="small"
            fullWidth
            slotProps={{
              input: {
                readOnly: !editing,
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
          <TextField
            label="Phone Number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            error={!!phoneError}
            helperText={phoneError}
            size="small"
            fullWidth
            slotProps={{
              input: {
                readOnly: !editing,
                sx: { fontSize: 14, color: "#1a1a1a" },
              },
            }}
          />
        </div>

        <div className="mb-6 flex justify-end">
          <Button
            variant="contained"
            size="small"
            onClick={() => setEditing(!editing)}
            sx={{
              textTransform: "none",
              bgcolor: editing ? "#e1b3f6" : "#e1b3f6",
              fontWeight: 600,
              fontSize: 12,
              borderRadius: "6px",
              px: 3,
              "&:hover": { bgcolor: editing ? "#e1b3f6" : "#e1b3f6" },
            }}
          >
            {editing ? "Save Changes" : "Edit Profile"}
          </Button>
        </div>

        <h3 className="mb-3 text-base font-bold " style={{color: "#1a1a1a"}}>
          Password and Authentication
        </h3>
        <div className="flex items-center gap-2 rounded-lg border-2 border-primary/40 bg-primary/5 px-4 py-3" style ={{ border: "2px solid #4caf50", background: "#f0fdf4" }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          <Chip
            label="Multi-factor authentication enabled"
            size="small"
            sx={{
              bgcolor: "transparent",
              color: "#4caf50",
              fontWeight: 600,
              fontSize: 13,
            }}
          />
        </div>
      </div>
    </section>
  )
}

/* ── Authorized Access ── */
function AuthorizedAccessSection() {
  return (
    <section id="authorized-access" className="scroll-mt-8">
      <h2 className="mb-1 text-xl font-bold" style={{ color: "#1a1a1a" }}>
        Authorized Access
      </h2>
      <p className="mb-4 text-sm leading-relaxed" style={{ color: "#6b7280" }}>
        These are the users you have given access to to view your data real-time
      </p>

      <div className="flex items-center justify-between rounded-xl px-5 py-4" style={{ border: "1px solid #d1d5db", background: "#fff" }}>
        <div className="flex items-center gap-3">
          <Avatar
            sx={{
              width: 42,
              height: 42,
              bgcolor: "#f3f4f6",
              color: "#9ca3af",
              fontSize: 16,
              fontWeight: 600,
            }}
          >
            D
          </Avatar>
          <div>
            <p className="text-sm font-semibold" style={{ color: "#1a1a1a" }}>Dr. User 1</p>
            <Chip
              label="ONLINE"
              size="small"
              sx={{
                bgcolor: "#e8f5e9",
                color: "#2e7d32",
                fontWeight: 700,
                fontSize: 10,
                height: 20,
                mt: 0.5,
              }}
            />
          </div>
        </div>
        <Button
          variant="contained"
          size="small"
          sx={{
            textTransform: "none",
            bgcolor: "#FF6363",
            fontWeight: 700,
            fontSize: 11,
            borderRadius: "16px",
            px: 2.5,
            "&:hover": { bgcolor: "#FF6363" },
          }}
        >
          Remove
        </Button>
      </div>
    </section>
  )
}
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


/* ── Appearance ─────────────────────────────────────── */
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

/* ── Goals ──────────────────────────────────────────── */
const goals = [
  {
    iconSrc: "/Steps_Icon.svg",
    label: "Steps",
    value: "10,000 per day",
    highlighted: false,
  },
  {
    iconSrc: "/Calories_Icon.svg",
    label: "Calories Burned",
    value: "500 per day",
    highlighted: false,
  },
]

function GoalsSection() {
  return (
    <section id="goals" className="scroll-mt-8">
      <h2 className="mb-4 text-lg font-bold" style={{ color: "#1a1a1a" }}>Goals</h2>
      <div className="flex flex-col gap-3">
        {goals.map((goal) => (
          <div
            key={goal.label}
            className="flex items-center justify-between rounded-xl px-5 py-4"
            style={{
              border: "2px solid #d1d5db",
              background: "#fff",
            }}
          >
            <div className="flex items-center gap-3">
              <Image src={goal.iconSrc} alt={goal.label} width={24} height={24} />
              <span className="text-sm font-bold" style={{ color: "#1a1a1a" }}>
                {goal.label}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm" style={{ color: "#6b7280" }}>
                {goal.value}
              </span>
              <Button
                variant="contained"
                size="small"
                sx={{
                  textTransform: "none",
                  bgcolor: "#e1b3f6",
                  fontWeight: 700,
                  fontSize: 11,
                  borderRadius: "12px",
                  px: 2,
                  minWidth: "auto",
                  "&:hover": { bgcolor: "#e1b3f6" },
                }}
              >
                EDIT
              </Button>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ── Notifications ──────────────────────────────────── */
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

/* ── Main Settings Page ─────────────────────────────── */
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
              <AuthorizedAccessSection />
              <DataPrivacySection />
              <hr style={{ borderColor: "#e5e7eb" }} />
              <AppearanceSection />
              <hr style={{ borderColor: "#e5e7eb" }} />
              <GoalsSection />
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
