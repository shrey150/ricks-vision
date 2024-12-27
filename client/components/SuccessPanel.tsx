import { Button } from "@/components/ui/button"
import { TreePalmIcon as PalmTree, Download } from 'lucide-react'

export default function SuccessPanel() {
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
        Thanks! You'll get a text shortly.
      </p>
      <p className="text-l italic text-zinc-300">
        You can also text Rick's Vision directly to get line updates. Try it out below!
      </p>
      <Button
        onClick={() => window.location.href = '/contact.vcf'}
        className="w-full h-12 text-lg bg-green-400 hover:bg-green-500 text-black font-medium shadow-lg shadow-green-400/30
          transition-all duration-300 hover:shadow-green-400/50 active:scale-95"
      >
        <Download className="h-5 w-5" />
        Save to your contacts
      </Button>
    </div>
  )
}

