"use client";
import Link from "next/link";
import { Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 md:p-8 bg-[linear-gradient(to_right,#71E4FD,#B2C4FE,#D3B5FF,#FAB9D0)] ">
      
      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-6xl overflow-hidden">
        
        {/* Grid Layout - stacks on mobile, side-by-side on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2">
          
          {/* Left Content */}
          <div className="p-8 sm:p-10 md:p-12 lg:p-16 flex flex-col justify-center">
            
            {/* Logo and App Name */}
            <div className="flex items-center gap-2 mb-8">
              <img src="/PulseLink_logo.svg" alt="PulseLink Logo" className="w-20 h-20" />
              <h2 className="text-2xl font-semibold text-gray-800">
                PulseLink
              </h2>
            </div>
            
            {/* Main Heading */}
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
              Want to start your personalized health journey?
            </h1>
            
            {/* Subtitle */}
            <p className="text-base sm:text-lg text-gray-600 leading-relaxed mb-8">
              Welcome to PulseLink. Track your wellness with personalized insights from your health-care professional.
            </p>
            
            {/* Get Started Button */}
            <div>
              <Button
                variant="contained"
                onClick={() => router.push("/auth/signup")}
                sx={{
                  background: "#E1B3F6",
                  borderRadius: "12px",
                  paddingX: 4,
                  paddingY: 1.5,
                  fontSize: "1.125rem",
                  fontWeight: 600,
                  textTransform: "none",
                  boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                  "&:hover": {
                    background: "#d09ff0",
                    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                  }
                }}
              >
                Get Started
              </Button>
            </div>
          </div>
          
          {/* Right Illustration */}
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-8 sm:p-10 md:p-12 lg:p-16 flex items-center justify-center min-h-[400px] md:min-h-full">
            <div className="w-full h-full flex items-center justify-center">
              {/* Replace this placeholder with your mascot image */}
              <div className="border-[3px] border-dashed border-gray-300 rounded-2xl flex items-center justify-center bg-white/50 w-full h-full min-h-[300px]">
                <p className="text-gray-400 text-center p-4 text-sm">
                  Mascot Image Placeholder
                  <br />
                  <span className="text-xs">(Add your image here)</span>
                </p>
              </div>
              {/* When you're ready, replace the placeholder with:
              <img 
                src="/path-to-your-mascot.png" 
                alt="PulseLink Mascot" 
                className="w-full h-full object-contain max-w-md"
              />
              */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}