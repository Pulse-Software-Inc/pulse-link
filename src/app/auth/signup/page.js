'use client';
{/* Frontend Compenents */ }
import UserHeader from "@/components/basics/UserHeader"
import FormButton from "@/components/basics/FormButton"
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

{/* Firebase JS SDK For Authentication */ }
import { auth } from '@/lib/firebase';
import { createUserWithEmailAndPassword, deleteUser } from 'firebase/auth';

export default function SignUpPage() {
  {/* Constant tailwind styling configurations used in Form */ }
  const boxLabelStyling = 'block text-xs text-gray-500 mb-1'
  const inputBoxStyling = "w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
  const router = useRouter()

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

  const handleRoleChange = (newRole) => {
    setFormData((prev) => ({ ...prev, role: newRole }));
  };

  const returnToggleStyling = (option) => {
    const styling = (option == formData.role) ? 'bg-white text-gray-800 shadow-sm' : 'bg-transparent text-gray-500'
    return styling
  }

  const handleSubmit = async (e) => {
    // e.preventDefault();

    // let createdUser = null;

    // try {
    //   const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
    //   createdUser = userCredential.user;
    //   const idToken = await createdUser.getIdToken();
    //   const response = await fetch('http://localhost:8000/api/v1/users/me', {
    //     method: 'PUT',
    //     headers: {
    //       'Authorization': `Bearer ${idToken}`,
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({
    //       firstName: formData.firstName,
    //       lastName: formData.lastName,
    //       email: formData.email,
    //       role: formData.role
    //     }),
    //   });

    //   if (!response.ok) {
    //     throw new Error();
    //   }

    //   router.push('/auth/login');
    // } catch {
    //   if (createdUser) {
    //     try {
    //       await deleteUser(createdUser);
    //     } catch {}
    //   }
    // }

    // For Testing As Approved By Prof Ali
    router.push('/auth/login')
  };

  return (
    <div className="min-h-screen justify-center p-4 bg-[linear-gradient(to_bottom_right,#ECB6E6,#D3B5FF,#B2C4FE,#71E4FD)]">
      {/* Logo in top left */}
      <UserHeader />

      {/* Centered Card */}
      <main className="flex items-center justify-center min-h-screen py-20">
        <div className="w-full max-w-md mx-auto px-8 py-12 rounded-3xl shadow-xl bg-white my-8">
          {/* Title */}
          <div className="mb-6 mt-4">
            <h1 className="text-3xl font-bold text-gray-800 mb-1">Sign Up</h1>
            <p className="text-gray-500 text-sm">
              Track your health journey with PulseLink
            </p>
          </div>

          {/* Role Toggle */}
          <div className=" mb-6 bg-gray-100 rounded-xl p-[3px] grid grid-cols-2 gap-1">
            <button
              type="button"
              onClick={() => handleRoleChange('user')}
              className={`py-2 px-6 text-sm font-medium rounded-lg transition-all ${returnToggleStyling('user')}`}
            >
              User
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('professional')}
              className={`py-2 px-6 text-sm font-medium rounded-lg transition-all ${returnToggleStyling('professional')}`}
            >
              Professional
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* First Name and Last Name Row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={boxLabelStyling}>First name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                  className={inputBoxStyling}
                />
              </div>
              <div>
                <label className={boxLabelStyling}>Last name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                  className={inputBoxStyling}
                />
              </div>
            </div>

            {/* Age & Gender Row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={boxLabelStyling}>Age</label>
                <input
                  type="text"
                  name="age"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                  className={inputBoxStyling}
                />
              </div>
              <div>
                <label className={boxLabelStyling}>Gender</label>
                <input
                  type="text"
                  name="gender"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                  className={inputBoxStyling}
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className={boxLabelStyling}>Email address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className={inputBoxStyling}
              />
            </div>

            {/* Password Field */}
            <div>
              <label className={boxLabelStyling}>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className={inputBoxStyling}
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
                I Accept The Terms and Conditions
              </label>
            </div>

            {/* Sign Up Button */}
            <FormButton text='Sign Up' />
          </form>


          {/* Login Link */}
          <p className="text-center mt-6 mb-4 text-sm text-gray-600">
            Already have an account?
            <Link
              href="/auth/login"
              className="text-[#EBD8FF] font-medium hover:text-[#D7B2FF]"
            >
              {' Login'}
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
