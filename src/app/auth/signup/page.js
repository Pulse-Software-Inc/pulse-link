import React from 'react';
import ExampleButton from "@/components/ExampleButton.js"
import Link from 'next/link'

export default function Page() {
  return (
    <main>
      <h1>Page Title</h1>
      <p>This is a server component. It renders on the server.</p>
      <ExampleButton />
      <Link href="/"> Home </Link>
    </main>
  );
}