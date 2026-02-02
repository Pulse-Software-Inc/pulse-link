/* GET STARTED PAGE */
import UserHeader from "@/components/UserHeader.js"
import Link from 'next/link'
import SignupBox from "@/components/GetStarted.js"
import Image from 'next/image'

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #88d5f5 0%, #f5a4c8 100%)',
      padding: '20px',
      position: 'relative'
    }}>
      <UserHeader />
      <SignupBox />
    </div>
  );
}
