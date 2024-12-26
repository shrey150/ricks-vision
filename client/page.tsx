'use client'

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TreePalmIcon as PalmTree } from 'lucide-react'
import { useState } from 'react'

export default function LandingPage() {
  const [phone, setPhone] = useState('')
  const [isValid, setIsValid] = useState(false)

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digits
    const cleaned = value.replace(/\D/g, '')
    
    // Format the number
    let formatted = cleaned
    if (cleaned.length > 3) {
      formatted = `${cleaned.slice(0, 3)}-${cleaned.slice(3)}`
    }
    if (cleaned.length > 6) {
      formatted = `${formatted.slice(0, 7)}-${formatted.slice(7)}`
    }
    
    return formatted
  }

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value
    const previousInput = phone
    
    // Allow backspacing over hyphens
    if (input.length < previousInput.length) {
      if (previousInput.endsWith('-') && !input.endsWith('-')) {
        setPhone(input.slice(0, -1))
      } else {
        setPhone(input)
      }
    } else {
      const formattedNumber = formatPhoneNumber(input)
      setPhone(formattedNumber)
    }
    
    // Check if it's a valid 10-digit number
    const digitsOnly = input.replace(/\D/g, '')
    setIsValid(digitsOnly.length === 10)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isValid) {
      // Handle form submission
      console.log('Valid phone number:', phone)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-900 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background glow */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-red-500/10 animate-pulse" />
      
      {/* Brick texture overlay */}
      <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGRlZnM+PHBhdHRlcm4gaWQ9ImJyaWNrIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiPjxwYXRoIGQ9Ik0wIDBoNDB2NDBIMHoiIGZpbGw9IiMwMDAiLz48cGF0aCBkPSJNMCAwaDQwdjIwSDB6IiBmaWxsPSIjMjIyIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2JyaWNrKSIvPjwvc3ZnPg==')]" />

      <main className="max-w-md w-full space-y-8 bg-black/40 backdrop-blur-sm p-8 rounded-lg border border-white/10 shadow-2xl relative z-10">
        <div className="text-center space-y-4">
          {/* Logo section */}
          <div className="relative inline-block">
            <PalmTree className="h-12 w-12 text-green-400 absolute -right-8 -top-6 transform rotate-12" />
            <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-600 
              [text-shadow:0_0_20px_theme(colors.red.500/40)] animate-pulse">
              Rick's Vision
            </h1>
          </div>
          <p className="text-xl text-blue-400 [text-shadow:0_0_10px_theme(colors.blue.400/40)]">
            Get texts on how the line is looking
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <Input
              id="phone-number"
              name="phone"
              type="tel"
              required
              value={phone}
              onChange={handlePhoneChange}
              className="bg-white/10 border-white/20 text-white placeholder-white/50 backdrop-blur-sm"
              placeholder="123-456-7890"
            />
            {phone && !isValid && (
              <p className="text-red-400 text-sm">Please enter a valid 10-digit phone number</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={!isValid}
            className="w-full bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/30
              transition-all duration-300 hover:shadow-red-500/50 hover:scale-[1.02]
              disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-red-500/30"
          >
            Notify me
          </Button>
        </form>

        <p className="text-center text-sm text-zinc-400">
          By providing your information you opt in to receiving texts from our service. 
          Messaging rates may apply.
        </p>
      </main>

      {/* Decorative light beams */}
      <div className="absolute bottom-0 left-1/4 w-1 h-[30vh] bg-blue-500/20 rotate-45 blur-xl" />
      <div className="absolute bottom-0 right-1/4 w-1 h-[30vh] bg-red-500/20 -rotate-45 blur-xl" />
    </div>
  )
}

