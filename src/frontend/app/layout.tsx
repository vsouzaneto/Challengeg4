import React from "react"
import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const inter = Inter({
  subsets: ["latin"],
  variable: '--font-g4s-sans',
  weight: ["200", "400", "500"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: '--font-g4s-mono',
  display: "swap",
});

const g4Description =
  "G4 reúne conhecimento, execução e conexões em um único ecossistema para orientar líderes que constroem empresas reais com método, disciplina e ambição."

export const metadata: Metadata = {
  metadataBase: new URL("https://g4business.com"),
  title: {
    default: "G4 | Para quem quer mais",
    template: "%s | G4",
  },
  description: g4Description,
  robots: {
    index: true,
    follow: true,
    "max-snippet": -1,
    "max-video-preview": -1,
    "max-image-preview": "large",
  },
  alternates: {
    canonical: "https://g4business.com",
  },
  openGraph: {
    locale: "pt_BR",
    type: "website",
    title: "G4 | Para quem quer mais",
    description: g4Description,
    url: "https://g4business.com",
    siteName: "G4",
  },
  twitter: {
    card: "summary_large_image",
    title: "G4 | Para quem quer mais",
    description: g4Description,
  },
  icons: {
    icon: [
      { url: "/brand/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/brand/favicon-192x192.png", sizes: "192x192", type: "image/png" },
    ],
    apple: [{ url: "/brand/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  other: {
    "twitter:label1": "Escrito por",
    "twitter:data1": "ferramentas@g4educacao.com",
    "twitter:label2": "Tempo para leitura",
    "twitter:data2": "7 minutos",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  // suppressHydrationWarning on <html> / <body> tolerates browser extensions
  // (e.g. the Cursor IDE's MCP) that inject data-* attributes into the
  // SSR-rendered HTML before React hydrates.
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <meta property="og:updated_time" content="2026-09-17T09:26:50-03:00" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
        suppressHydrationWarning
      >
        {children}
        <Analytics />
      </body>
    </html>
  )
}
