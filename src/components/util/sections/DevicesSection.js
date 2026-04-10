'use client';

import {useState} from 'react';
import Image from 'next/image';

export default function DevicesSection(props) {
  const formData = props.formData;
  const updateField = props.updateField;

  const connectedDevices = formData.devices.filter(d => d.is_active).length
  const lastSynced = formData.devices.find(d => d.last_sync)?.last_sync ?? "Never"
  const [showModal, setShowModal] = useState(false)

  const unsyncDevice = (deviceId) =>
    updateField("devices", formData.devices.filter(d => d.device_id !== deviceId))

  const connectDevice = (device) => {
    updateField("devices", [...formData.devices, { ...device, is_active: true }])
    updateField("available_devices", formData.available_devices.filter(d => d.device_id !== device.device_id))
    setShowModal(false)
  }
  return (
    <div id="devices" className="flex-1">
      <h2 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}> Devices </h2>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="flex flex-col justify-between border border-gray-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-500">Connected Devices</span>
            <Image src="/Sidebar/Devices_Icon.svg" alt="Devices" width={18} height={18} className="opacity-40" />
          </div>
          <p className="text-3xl font-semibold text-gray-900">{connectedDevices}</p>
        </div>

        <div className="flex flex-col justify-between border border-gray-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-500">Last Synced</span>
            <Image src="/DashboardIcons/Synced_Icon.svg" alt="Last Synced" width={18} height={18} className="opacity-40" />
          </div>
          <p className="text-xl font-semibold text-gray-900">{lastSynced}</p>
        </div>
      </div>

      <hr className="border-gray-200 mb-6" />

      <h3 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}> Device List </h3>
      <div className="space-y-3">
        {formData.devices.map((device) => (
          <div key={device.device_id} className="flex items-center justify-between border border-gray-200 rounded-xl px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Image src="/Sidebar/Devices_Icon.svg" alt="Device" width={16} height={16} className="opacity-50" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{device.device_name}</p>
                <p className="text-xs text-gray-400">
                  {device.last_sync ? `Last Sync ${device.last_sync}` : "Never synced"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {
                <button
                  type="button"
                  onClick={() => unsyncDevice(device.device_id)}
                  className="px-4 py-1.5 rounded-full text-xs font-medium text-white bg-gradient-to-r from-[#B2C4FE] to-[#ECB6E6] hover:opacity-90 transition-opacity"
                >
                  unsync
                </button>
              }
              <div className="text-right">
                <p className="text-xs text-gray-400 mb-1">Status</p>
                {device.is_active
                  ? <span className="px-3 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-700">CONNECTED</span>
                  : <span className="px-3 py-1 rounded-md text-xs font-semibold bg-gray-200 text-gray-500">DISCONNECTED</span>
                }
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Connect More */}
      {formData.available_devices.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-4">No devices available.</p>
      ) : (
        formData.available_devices.map(device => (
          <div key={device.device_id} className="flex items-center justify-between px-4 py-3 border border-gray-200 rounded-xl">
            <div>
              <p className="text-sm font-medium text-gray-900">{device.device_name}</p>
              <p className="text-xs text-gray-400">{device.brand} · {device.device_type}</p>
            </div>
            <button
              type="button"
              onClick={() => connectDevice(device)}
              className="px-4 py-1.5 rounded-full text-xs font-medium text-white bg-gradient-to-r from-[#B2C4FE] to-[#ECB6E6]"
            >
              CONNECT
            </button>
          </div>
        ))
      )}
    </div>
  );
}