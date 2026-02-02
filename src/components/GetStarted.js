import { Box,Button } from "@mui/material";
import Link from "next/link";

export default function SignupBox() {
    return (
    <main style={{
        maxWidth: '600px',
        margin: '0 auto',
        padding: '40px 20px',
        backgroundColor: 'white',
        borderRadius: '12px',
        marginTop: '40px'
      }}>
        <h1 style={{ textAlign: 'center', marginBottom: '20px', color: '#333' }}>Get Started</h1>
        <div style={{ marginTop: '20px', display: 'flex', gap: '15px', justifyContent: 'center' }}>
          <Button href="/auth/signup" style={{
            padding: '15px 30px',
            backgroundColor: '#88d5f5',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '18px',
            fontWeight: '500'
          }}> Sign up
          </Button>
          <Button href = "/auth/login" style={{
            padding: '15px 30px',
            backgroundColor: '#f5a4c8',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '18px',
            fontWeight: '500'
          }}>
            Login
          </Button>
        </div>
      </main>
    );
}
