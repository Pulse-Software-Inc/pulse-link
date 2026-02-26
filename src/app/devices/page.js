"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Sidebar from "@/components/Sidebar"

export default function DevicesPage() {
  const [devices, setDevices] = useState([])
  const [stats, setStats] = useState({ connected: 0, synced: 0, lastSynced: 0 })

  useEffect(() => {
    fetch("/userdata.json")
      .then((res) => res.json())
      .then((data) => {
        const deviceList = data.devices || []
        setDevices(deviceList)
        
        const connected = deviceList.filter((d) => d.is_active).length
        const synced = deviceList.length
        const lastSyncTimes = deviceList
          .map((d) => new Date(d.last_sync).getTime())
          .filter((t) => !isNaN(t))
        const mostRecentSync = lastSyncTimes.length > 0 
          ? Math.floor((Date.now() - Math.max(...lastSyncTimes)) / (1000 * 60 * 60))
          : 0
        
        setStats({ connected, synced, lastSynced: mostRecentSync })
      })
      .catch((err) => console.error("Failed to load devices:", err))
  }, [])

  const formatLastSync = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffHours < 1) return "Just now"
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays === 1) return "Yesterday"
    return `${diffDays} days ago`
  }

  const getDeviceIcon = (type) => {
    switch (type) {
      case "fitness_tracker":
        return "/Devices_Icon.svg"
      case "smartphone":
        return "/Devices_Icon.svg"
      default:
        return "/Devices_Icon.svg"
    }
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      
      <main className="flex-1 p-8">
        <div className="flex items-center gap-4 mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Devices</h1>
          <Image src="/PulseLink_logo.svg" alt="PulseLink" width={40} height={40} />
        </div>

        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-2">
              <Image src="/Devices_Icon.svg" alt="Connected" width={20} height={20} className="opacity-60" />
              <span className="text-sm text-gray-500">Connected Devices</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.connected}</p>
          </div>
          
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-2">
              <Image src="/Synced_Icon.svg" alt="Synced" width={20} height={20} className="opacity-60" />
              <span className="text-sm text-gray-500">Synced Metrics</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.synced}</p>
          </div>
          
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-2">
              <Image src="/Synced_Icon.svg" alt="Last Synced" width={20} height={20} className="opacity-60" />
              <span className="text-sm text-gray-500">Last Synced</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.lastSynced} <span className="text-lg font-normal text-gray-500">hours</span></p>
          </div>
        </div>

        <div className="space-y-4">
          {devices.map((device) => (
            <div
              key={device.id}
              className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#71E4FD] to-[#ECB6E6] flex items-center justify-center">
                  <Image src={getDeviceIcon(device.device_type)} alt={device.device_name} width={24} height={24} className="invert" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{device.device_name}</h3>
                  <p className="text-sm text-gray-500">Last synced: {formatLastSync(device.last_sync)}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  device.is_active 
                    ? "bg-green-100 text-green-700" 
                    : "bg-gray-100 text-gray-500"
                }`}>
                  {device.is_active ? "Active" : "Inactive"}
                </span>
                
                <button className="px-4 py-2 bg-gradient-to-r from-[#71E4FD] via-[#B2C4FE] to-[#ECB6E6] text-white rounded-lg font-medium hover:opacity-90 transition-opacity">
                  Sync
                </button>
                
                <button className="px-4 py-2 border border-red-300 text-red-500 rounded-lg font-medium hover:bg-red-50 transition-colors">
                  Disconnect
                </button>
              </div>
            </div>
          ))}
        </div>

        <button className="mt-6 w-full py-4 border-2 border-dashed border-gray-300 rounded-2xl text-gray-500 font-medium hover:border-[#B2C4FE] hover:text-[#B2C4FE] transition-colors">
          + Add New Device
        </button>
      </main>
    </div>
  )
}