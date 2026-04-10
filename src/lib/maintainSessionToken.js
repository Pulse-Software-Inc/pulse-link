"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { onAuthStateChanged, signOut as firebaseSignOut } from "firebase/auth"
import { auth } from "@/lib/firebase"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [idToken, setIdToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        const token = await firebaseUser.getIdToken()
        setUser(firebaseUser)
        setIdToken(token)
      } else {
        setUser(null)
        setIdToken(null)
      }
      setLoading(false)
    })
    return () => unsubscribe()
  }, [])

  const signOut = () => firebaseSignOut(auth)   // clears user + token automatically

  return (
    <AuthContext.Provider value={{ user, idToken, signOut, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)