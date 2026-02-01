/* GET STARTED PAGE */
import ExampleButton from "@/components/ExampleButton.js"
import UserHeader from "@/components/UserHeader.js"
import Link from 'next/link'

export default function Home() {
  return (
    <div>
      <UserHeader />
      <main>
        <ExampleButton />
        <Link href="/auth/signup"> Signup's </Link>
        <Link href="/auth/login"> Login </Link>
      </main>
    </div>
  );
}
