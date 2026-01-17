// frontend/app/layout.tsx
import "./globals.css"
import { ReactNode } from "react"

export const metadata = {
  title: "Trade Journal",
  description: "Intraday Trading Journal",
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
