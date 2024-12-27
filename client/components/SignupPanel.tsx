'use client'

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TreePalmIcon as PalmTree, Loader2 } from 'lucide-react'
import { useState } from 'react'

interface SignupPanelProps {
  onSuccess: () => void;
  onError: (error: Error) => void;
}

export default function SignupPanel({ onSuccess, onError }: SignupPanelProps) {
  const [phone, setPhone] = useState('')
  const [isValid, setIsValid] = useState(false)
  const [attempted, setAttempted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const formatPhoneNumber = (value: string) => {
    const cleaned = value.replace(/\D/g, '')
    const limited = cleaned.slice(0, 10)
    
    let formatted = limited
    if (limited.length > 3) {
      formatted = `${limited.slice(0, 3)}-${limited.slice(3)}`
    }
    if (limited.length > 6) {
      formatted = `${formatted.slice(0, 7)}-${formatted.slice(7)}`
    }
    
    return formatted
  }

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value
    const previousInput = phone
    
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
    
    const cleaned = input.replace(/\D/g, '')
    const limited = cleaned.slice(0, 10)
    setIsValid(limited.length === 10)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAttempted(true);
    
    if (isValid) {
      setIsLoading(true);
      try {
        const response = await fetch('/api/subscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ phone }),
        });

        if (!response.ok) {
          throw new Error('Failed to subscribe');
        }

        onSuccess();
      } catch (error) {
        onError(error as Error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="text-center space-y-6">
      <div className="relative inline-block">
        <PalmTree className="h-12 w-12 text-green-400 absolute -right-8 -top-6 transform rotate-12" />
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-600 
          [text-shadow:0_0_20px_theme(colors.red.500/40)] animate-pulse">
          Rick's Vision
        </h1>
      </div>
      <p className="text-xl text-blue-400 [text-shadow:0_0_10px_theme(colors.blue.400/40)]">
        Get texts on how the line is looking
      </p>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <Input
            id="phone-number"
            name="phone"
            type="tel"
            required
            value={phone}
            onChange={handlePhoneChange}
            className="h-12 text-lg bg-white/10 border-white/20 text-white placeholder-white/50 backdrop-blur-sm"
            placeholder="123-456-7890"
          />
          {attempted && !isValid && (
            <p className="text-red-400 text-sm px-1">Please enter a valid 10-digit phone number</p>
          )}
        </div>

        <Button
          type="submit"
          disabled={!isValid || isLoading}
          className="w-full h-12 text-lg bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/30
            transition-all duration-300 hover:shadow-red-500/50 active:scale-95
            disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-red-500/30"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            'Notify me'
          )}
        </Button>
      </form>

      <p className="text-center text-xs text-zinc-400 px-2">
        By providing your information you opt in to receiving texts from our service. 
        Messaging rates may apply.
      </p>
    </div>
  )
} 