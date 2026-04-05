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
import { SettingsSidebar } from "@/components/util/SettingsSidebar"

export default function Settings(props) {
  // GET current settings from backend
  const currentSettings = {}

  // Initial Configurations
  let sectionIDs = [
    "user-profile",
    "data-privacy",
    "appearance",
    "notifications"
  ]
  if (currentSettings.role == 'user')
    sectionIDs.push("goals", "custom-instructions")
  else
    sectionIDs.push("invite-clients")

  const [editing, setEditing] = useState(false)
  const [firstName, setFirstName] = useState("First Name")
  const [lastName, setLastName] = useState("Last Name")
  const [email, setEmail] = useState("**********@email.com")
  const [phone, setPhone] = useState("*********1234")
  const [emailError, setEmailError] = useState("")
  const [phoneError, setPhoneError] = useState("")

  // Handlers
  pass;

  return (
    <>
    </>
  );
}