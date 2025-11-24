import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Galileo Chatbot',
  description: 'Galileo Chatbot powered by Azure OpenAI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

