'use client';

import FormButton from "@/components/basics/FormButton"
import UserHeader from "@/components/basics/UserHeader"
import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

{/* Firebase JS SDK For Authentication */ }
import { auth } from '@/lib/firebase';
import { signInWithEmailAndPassword } from 'firebase/auth';

export default function LoginPage() {
  const router = useRouter();
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
    acceptTerms: false,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Login attempt:', { loginData });
    // Only redirects when login is successful
    const userCredential = await signInWithEmailAndPassword(auth, loginData.email, loginData.password); // Mention Firebase Security Features, Fails if Email exists
    const idToken = await userCredential.user.getIdToken();
    const response = await fetch('http://localhost:8000/api/v1/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    console.log(data);

    if (response.ok) {
      router.push('/auth/login');
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Side - Gradient Background */}
      <div className="hidden lg:flex lg:w-1/2 bg-[linear-gradient(to_bottom_right,#ECB6E6,#D3B5FF,#B2C4FE,#71E4FD)] relative">
        {/* Logo in top left - consistent with signup page */}
        <div className="absolute top-6 left-6 flex items-center gap-3 z-10">
          <UserHeader />
        </div>
        {/* Main Content positioned at bottom */}
        <div className="text-white absolute bottom-8 left-12 right-12">
          <h1 className="text-5xl font-bold mb-6">Your health journey is here</h1>
          <p className="text-2xl font-light opacity-90 max-w-md">
            continue to track your wellness, monitor your progress, and achieve your health goals with personalized insights.
          </p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-xl">
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
                placeholder="john@gmail.com"
                value={loginData.email}
                onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
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
                placeholder="••••••••••"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                required
              />
            </div>

            {/* Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="terms"
                className="w-4 h-4 border-2 border-gray-300 rounded"
              />
              <label htmlFor="terms" className="ml-2 text-sm text-gray-700">
                I accept the Terms and Conditions
              </label>
            </div>

            {/* Login Button */}
            <FormButton text='Log In' />

            {/* Create Account Link */}
            <p className="text-center text-sm text-gray-600 mt-6">
              New to PulseLink?
              <Link href="/auth/signup" className="text-[#D7B2FF] font-medium">
                {' Create an Account'}
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}