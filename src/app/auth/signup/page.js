'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

export default function SignUpPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    role: 'user',
    acceptTerms: false,
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleRoleChange = (event, newRole) => {
    if (newRole !== null) {
      setFormData((prev) => ({ ...prev, role: newRole }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <div className="min-h-screen justify-center p-4 bg-[linear-gradient(to_bottom_right,#ECB6E6,#D3B5FF,#B2C4FE,#71E4FD)]">
      {/* Logo in top left */}
      <div className="absolute top-6 left-6 flex items-center gap-3 z-10">
        <Image src="/PulseLink_logo.svg" alt="PulseLink" width={100} height={100} />
        <span className="text-white font-bold text-4xl">PulseLink</span>
      </div>

      {/* Centered Card */}
      <div className="flex items-center justify-center min-h-screen py-20">
        <div className="w-1/3 min-w-[250px] px-8 py-12 rounded-3xl shadow-xl bg-white my-8">
          {/* Title */}
          <div className="mb-6 mt-4">
            <h1 className="text-3xl font-bold text-gray-800 mb-1">Sign Up</h1>
            <p className="text-gray-500 text-sm">
              Track your health journey with PulseLink
            </p>
          </div>

          {/* Role Toggle */}
          <div className="mb-6">
            <div className="bg-gray-100 rounded-xl p-[3px] grid grid-cols-2 gap-1">
              <button
                type="button"
                onClick={() => handleRoleChange(null, 'user')}
                className={`py-2 px-6 text-sm font-medium rounded-lg transition-all ${
                  formData.role === 'user'
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'bg-transparent text-gray-500'
                }`}
              >
                User
              </button>
              <button
                type="button"
                onClick={() => handleRoleChange(null, 'professional')}
                className={`py-2 px-6 text-sm font-medium rounded-lg transition-all ${
                  formData.role === 'professional'
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'bg-transparent text-gray-500'
                }`}
              >
                Professional
              </button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* First Name and Last Name Row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">First name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Last name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Email address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
              />
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
              />
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                name="acceptTerms"
                checked={formData.acceptTerms}
                onChange={handleInputChange}
                required
                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <label className="text-sm text-gray-700">
                I accept the Terms and Conditions
              </label>
            </div>

            {/* Sign Up Button */}
            <button
              type="submit"
              className="w-full py-3 text-sm font-semibold text-white rounded-xl shadow-md mt-2 transition-colors bg-[#D7B2FF] hover:bg-[#C89EFF]"
            >
              SIGN IN
            </button>
          </form>

          {/* Login Link */}
          <div className="text-center mt-6 mb-4">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                href="/auth/login"
                className="text-[#EBD8FF] font-medium hover:text-[#D7B2FF]"
              >
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}