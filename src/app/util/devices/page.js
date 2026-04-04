'use client';

import React from 'react';
import Image from 'next/image';
import Sidebar from '@/components/nav/SideBar';

export default function DevicesPage() {
  return (
    <div className="flex min-h-screen bg-white">
      <Sidebar />

      <main className="flex-1 p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-4">
          <h1 className="text-2xl font-semibold text-gray-900">Devices</h1>
          <Image src="/PulseLink_logo.svg" alt="PulseLink" width={44} height={44} />
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="border border-gray-200 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500">Connected Devices</span>
              <Image src="/Sidebar/Devices_Icon.svg" alt="Devices" width={18} height={18} className="opacity-40" />
            </div>
            <p className="text-3xl font-semibold text-gray-900">2</p>
          </div>

          <div className="border border-gray-200 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500">Synced Metrics</span>
              <Image src="/DashboardIcons/Synced_Icon.svg" alt="Synced" width={18} height={18} className="opacity-40" />
            </div>
            <p className="text-3xl font-semibold text-gray-900">3 <span className="text-base font-normal text-gray-400">/3</span></p>
          </div>

          <div className="border border-gray-200 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500">Last Synced</span>
              <Image src="/DashboardIcons/Synced_Icon.svg" alt="Last Synced" width={18} height={18} className="opacity-40" />
            </div>
            <p className="text-3xl font-semibold text-gray-900">2 <span className="text-base font-normal text-gray-400">min ago</span></p>
          </div>
        </div>

        <hr className="border-gray-200 mb-6" />

        /* Device List */
        <div className="space-y-3">

          {/* No name watch */}
          <div className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Image src="/Sidebar/Devices_Icon.svg" alt="Device" width={16} height={16} className="opacity-50" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">No name watch</p>
                <p className="text-xs text-gray-400">Last Sync 2 min ago <span className="text-green-500">90%</span></p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-1.5 rounded-full text-xs font-medium text-white bg-gradient-to-r from-[#B2C4FE] to-[#ECB6E6] hover:opacity-90 transition-opacity">
                UNSYNC
              </button>
              <div className="text-right">
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <span className="px-3 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-700">CONNECTED</span>
              </div>
            </div>
          </div>

          {/* Phone */}
          <div className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Image src="/Sidebar/Devices_Icon.svg" alt="Device" width={16} height={16} className="opacity-50" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Phone</p>
                <p className="text-xs text-gray-400">Last Sync 2 min ago <span className="text-yellow-500">67%</span></p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-1.5 rounded-full text-xs font-medium text-white bg-gradient-to-r from-[#B2C4FE] to-[#ECB6E6] hover:opacity-90 transition-opacity">
                UNSYNC
              </button>
              <div className="text-right">
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <span className="px-3 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-700">CONNECTED</span>
              </div>
            </div>
          </div>

          {/* No name watch 2 */}
          <div className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Image src="/Sidebar/Devices_Icon.svg" alt="Device" width={16} height={16} className="opacity-50" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">No name watch 2</p>
                <p className="text-xs text-gray-400">Last Sync 5 days ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <span className="px-3 py-1 rounded-md text-xs font-semibold bg-gray-200 text-gray-500">DISCONNECTED</span>
              </div>
            </div>
          </div>

        </div>

        {/* Connect More */}
        <div className="flex justify-end mt-6">
          <button className="px-5 py-2 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-[#B2C4FE] to-[#ECB6E6] hover:opacity-90 transition-opacity">
            CONNECT MORE DEVICES
          </button>
        </div>
      </main>
    </div>
  );
}