"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function SignOutPage() {
  const router = useRouter()
  const [isSigningOut, setIsSigningOut] = useState(false)
  const [signedOut, setSignedOut] = useState(false)

  const handleSignOut = () => {
    setIsSigningOut(true)
    
    setTimeout(() => {
      setIsSigningOut(false)
      setSignedOut(true)
    }, 1000)
  }

  if (signedOut) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#71E4FD] via-[#B2C4FE] via-[#D3B5FF] to-[#ECB6E6] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md w-full text-center">
          <div className="w-20 h-20 mx-auto mb-6">
            <Image src="/PulseLink_logo.svg" alt="PulseLink" width={80} height={80} />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Sign Out Successful</h1>
          <p className="text-gray-600 mb-6">
            You have been successfully signed out. Hope to see you soon to continue your fitness journey!
          </p>
          
          <Link
            href="/"
            className="inline-block w-full py-3 bg-gradient-to-r from-[#71E4FD] via-[#B2C4FE] to-[#ECB6E6] text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
          >
            Return to Home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#71E4FD] via-[#B2C4FE] via-[#D3B5FF] to-[#ECB6E6] flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md w-full text-center">
        <div className="w-20 h-20 mx-auto mb-6">
          <Image src="/PulseLink_logo.svg" alt="PulseLink" width={80} height={80} />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">We are sorry to see you go :(</h1>
        <p className="text-gray-600 mb-6">
          Are you sure you want to sign out? You can always come back to continue your health journey.
        </p>
        
        <div className="space-y-3">
          <button
            onClick={handleSignOut}
            disabled={isSigningOut}
            className="w-full py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
          >
            {isSigningOut ? "Signing out..." : "Sign Out"}
          </button>
          
          <button
            onClick={() => router.back()}
            className="w-full py-3 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}