'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Login attempt:', { email, password, acceptTerms });
  };

  return (
    <div className="flex min-h-screen">
      {/* Logo in top left - consistent with signup page */}
      <div className="absolute top-6 left-6 flex items-center gap-3 z-10">
        <Image 
          src="/PulseLink_logo.svg" 
          alt="PulseLink Logo" 
          width={100} 
          height={100}
        />
        <span className="text-white text-4xl">PulseLink</span>
      </div>

      {/* Left Side - Gradient Background */}
      <div className="hidden lg:flex lg:w-1/2 bg-[linear-gradient(to_bottom_right,#ECB6E6,#D3B5FF,#B2C4FE,#71E4FD)] relative">
        {/* Main Content positioned at bottom */}
        <div className="text-white absolute bottom-8 left-12 right-12">
          <h1 className="text-5xl font-bold mb-6">Your health journey is here</h1>
          <p className="text-2xl font-light opacity-90 max-w-md">
            continue to track your wellness, monitor your progress, and achieve your health goals with personalized insights.
          </p>
          <div className="flex gap-2 mt-8">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <div className="w-2 h-2 bg-white/50 rounded-full"></div>
            <div className="w-2 h-2 bg-white/50 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-xl -ml-24">
          <div className="mb-8">
            <h2 className="text-3xl font-normal text-gray-800 mb-2">
              Login to your Account
            </h2>
            <p className="text-gray-500 text-sm">Continue your wellness journey</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm text-gray-600 mb-2">
                Email address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@gmail.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm text-gray-600 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                required
              />
            </div>

            {/* Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="terms"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="w-4 h-4 border-2 border-gray-300 rounded focus:ring-2 focus:ring-purple-400"
              />
              <label htmlFor="terms" className="ml-2 text-sm text-gray-700">
                I accept the Terms and Conditions
              </label>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-[#D7B2FF] text-white py-3 rounded-lg font-medium hover:bg-[#C89EFF] transition-all duration-200 shadow-md"
            >
              LOGIN
            </button>

            {/* Create Account Link */}
            <p className="text-center text-sm text-gray-600 mt-6">
              New to PulseLink?{' '}
              <Link href="/auth/signup" className="text-[#D7B2FF] font-medium">
                Create an Account
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}