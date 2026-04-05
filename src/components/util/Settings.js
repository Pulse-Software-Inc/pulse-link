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
import SettingsSidebar from "@/components/util/SettingsSidebar"
import UserProfileSection    from "./sections/UserProfileSection"
import AuthorizedAccessSection from "./sections/AuthorizedAccessSection"
import DataPrivacySection    from "./sections/DataPrivacySection"
import AppearanceSection     from "./sections/AppearanceSection"
import GoalsSection          from "./sections/GoalsSection"
import NotificationsSection  from "./sections/NotificationsSection"
import InviteClientsSection  from "./sections/InviteClientsSection"


export default function Settings(props) {
  // GET current settings from backend
  const currentSettings = {}

  // Initial Configurations
  let sidebarLabels = [
    { id: "user-profile", label: "User Profile" },
    { id: "authorized-access", label: "Authorized Access" },
    { id: "data-privacy", label: "Data and Privacy" },
    { id: "appearance", label: "Appearance" }
  ]
  if (currentSettings.role == 'user')
    sectionIDs.push({ id: "goals", label: "Goals" },
      { id: "notifications", label: "Notifications" })
  else
    sectionIDs.push({ id: "invite-clients", label: "Invite Clients" })

  // Handlers


  return (
    <>
    </>
  );
}