import ExampleButton from "@/components/ExampleButton.js"
import Link from 'next/link'

export default function Home() {
  return (
    <div>
      <main>
        <ExampleButton />
        <Link href="/auth/signup"> Signup's </Link>
        <Link href="/auth/login"> Login </Link>
      </main>
    </div>
  );
}
