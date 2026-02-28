"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function DeleteAccountPage() {
  const router = useRouter()
  const [confirmText, setConfirmText] = useState("")
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleted, setDeleted] = useState(false)

  const handleDelete = () => {
    if (confirmText !== "DELETE") return
    
    setIsDeleting(true)
    
    setTimeout(() => {
      setIsDeleting(false)
      setDeleted(true)
    }, 2000)
  }

  if (deleted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#71E4FD] via-[#B2C4FE] via-[#D3B5FF] to-[#ECB6E6] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md w-full text-center">
          <div className="w-20 h-20 mx-auto mb-6">
            <Image src="/PulseLink_logo.svg" alt="PulseLink" width={80} height={80} />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Account Deleted</h1>
          <p className="text-gray-600 mb-6">
            Your account and all associated data have been permanently deleted. We are sorry to see you go. To start your journey again, SIGN UP!
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
      <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md w-full">
        <button
          onClick={() => router.back()}
          className="mb-4 text-gray-500 hover:text-gray-700"
        >
          <Image src="/CrossX_Icon.svg" alt="Close" width={24} height={24} />
        </button>
        
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6">
            <Image src="/PulseLink_logo.svg" alt="PulseLink" width={80} height={80} />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">We are sorry to see you go :(</h1>
          <p className="text-gray-600 mb-6">
            Please note that deleting your account will remove all associated data and this action cannot be undone.
          </p>
          
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-left">
            <h3 className="font-semibold text-red-700 mb-2">This will permanently delete:</h3>
            <ul className="text-sm text-red-600 space-y-1">
              <li>- Your profile and personal information</li>
              <li>- All health data and biomarkers</li>
              <li>- Connected device data</li>
              <li>- Mood and companion history</li>
              <li>- Healthcare provider connections</li>
            </ul>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm text-gray-600 mb-2 text-left">
              Type <span className="font-bold">DELETE</span> to confirm:
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder="Type DELETE"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>
          
          <div className="space-y-3">
            <button
              onClick={handleDelete}
              disabled={confirmText !== "DELETE" || isDeleting}
              className="w-full py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDeleting ? "Deleting Account..." : "Permanently Delete Account"}
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
    </div>
  )
}