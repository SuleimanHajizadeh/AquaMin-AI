import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AquaMind AI — Ağıllı Akvakültur Monitorinqi',
  description: 'Azərbaycan Respublikası — Real vaxtlı su həyatı monitorinq sistemi',
  icons: { icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌊</text></svg>" }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="az">
      <body>{children}</body>
    </html>
  )
}
