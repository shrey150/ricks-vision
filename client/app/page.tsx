'use client'

import { useState } from 'react'
import { useToast } from "@/hooks/use-toast"
import SignupPanel from '@/components/SignupPanel'
import SuccessPanel from '@/components/SuccessPanel'

export default function LandingPage() {
  const [isSuccess, setIsSuccess] = useState(false)
  const { toast } = useToast()

  const handleSuccess = () => {
    toast({
      title: "You're on the list! 🎉",
      description: "We'll text you when the line is looking good!",
      duration: 5000,
    });
    setIsSuccess(true);
  }

  const handleError = (error: Error) => {
    console.error('Error:', error);
    toast({
      title: "Oops! Something went wrong",
      description: "Please try again later",
      variant: "destructive",
      duration: 5000,
    });
  }

  return (
    <div className="min-h-screen bg-zinc-900 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background glow */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-red-500/10 animate-pulse" />
      
      {/* Brick texture overlay */}
      <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGRlZnM+PHBhdHRlcm4gaWQ9ImJyaWNrIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiPjxwYXRoIGQ9Ik0wIDBoNDB2NDBIMHoiIGZpbGw9IiMwMDAiLz48cGF0aCBkPSJNMCAwaDQwdjIwSDB6IiBmaWxsPSIjMjIyIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2JyaWNrKSIvPjwvc3ZnPg==')]" />

      <main className="w-[min(100%,400px)] space-y-6 bg-black/40 backdrop-blur-sm p-6 rounded-lg border border-white/10 shadow-2xl relative z-10">
        {isSuccess ? (
          <SuccessPanel />
        ) : (
          <SignupPanel onSuccess={handleSuccess} onError={handleError} />
        )}
      </main>

      {/* Decorative light beams */}
      <div className="absolute bottom-0 left-1/4 w-1 h-[30vh] bg-blue-500/20 rotate-45 blur-xl" />
      <div className="absolute bottom-0 right-1/4 w-1 h-[30vh] bg-red-500/20 -rotate-45 blur-xl" />
    </div>
  )
}

