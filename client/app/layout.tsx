import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { CSPostHogProvider } from './providers';
import { Toaster } from "@/components/ui/toaster"

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Rick's Vision",
  description: "Get texts on how the line is looking",
  openGraph: {
    title: "Rick's Vision",
    description: "Get texts on how the line is looking",
    type: "website",
    images: [
      {
        url: '/opengraph-image',
        width: 1200,
        height: 630,
        alt: "Rick's Vision - Line Status Updates"
      }
    ],
    siteName: "Rick's Vision"
  },
  twitter: {
    card: "summary_large_image",
    title: "Rick's Vision",
    description: "Get texts on how the line is looking",
    images: ['/opengraph-image'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <CSPostHogProvider>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          {children}
          <Toaster />
        </body>
      </CSPostHogProvider>
    </html>
  );
}
