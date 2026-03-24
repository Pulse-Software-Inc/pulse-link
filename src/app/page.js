"use client";
import LinkButton from "@/components/basics/LinkButton"
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 md:p-8 bg-[linear-gradient(to_right,#71E4FD,#B2C4FE,#D3B5FF,#FAB9D0)] ">

      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-6xl overflow-hidden grid grid-cols-1 md:grid-cols-2">

        {/* Left Content */}
        <div className="p-8 sm:p-10 md:p-12 lg:p-16 flex flex-col justify-center">
          {/* Logo and App Name */}
          <div className="flex items-center gap-2 mb-8">
            <img src="/PulseLink_logo.svg" alt="PulseLink Logo" className="w-20 h-20" />
          </div>
          <h1 className="text-gray-600 text-1xl sm:text-4xl md:text-4xl font-bold leading-tight mb-6">
            Want to start your personalized health journey?
          </h1>
          <p className="text-base sm:text-lg text-gray-600 leading-relaxed mb-8 text-justify">
            Welcome to PulseLink. Track your wellness with personalized insights from your health-care professional.
          </p>

          {/* Get Started Button */}
          <LinkButton
            link="/auth/signup" fsize="1.125rem" fweight={600}
            borderRadius="12px" px={4} py={1.5} text="Get Started" />
        </div>

        {/* Right Content (Bloat Code To-Be-Replaced When Mascot Is Ready) */}
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
  );
}