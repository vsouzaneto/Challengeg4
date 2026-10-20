import type { Metadata } from "next";
import { Inter } from "next/font/google";
import type { ReactNode } from "react";

import { AppHeader } from "@/components/app/app-header";
import { ThemeProvider } from "@/components/app/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { BRAND } from "@/copy/pt-BR";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: { default: BRAND.name, template: `%s · ${BRAND.name}` },
  description: BRAND.tagline,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-svh">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <TooltipProvider>
            <AppHeader />
            <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
