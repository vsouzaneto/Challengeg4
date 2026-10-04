"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BookOpen, DatabaseZap, FlaskConical, Gauge, Inbox, Microscope, MonitorSmartphone, Workflow } from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/diagnostico", label: "Diagnóstico", icon: Microscope },
  { href: "/perguntas", label: "Pergunte aos dados", icon: DatabaseZap },
  { href: "/inbox", label: "Smart Inbox", icon: Inbox, badge: "inbox" },
  { href: "/simulador", label: "Simulador do cliente", icon: MonitorSmartphone },
  { href: "/knowledge", label: "Knowledge Base", icon: BookOpen, badge: "knowledge" },
  { href: "/confianca", label: "Confiança da IA", icon: Gauge },
  { href: "/evals", label: "Evals", icon: FlaskConical },
  { href: "/arquitetura", label: "Como funciona", icon: Workflow },
] as const;

export function NavLinks({ badges }: { badges: Record<string, number> }) {
  const path = usePathname();
  return (
    <nav className="mt-8 space-y-1">
      {NAV.map(({ href, label, icon: Icon, ...rest }) => {
        const active = path.startsWith(href);
        const badge = "badge" in rest ? badges[rest.badge] : 0;
        return (
          <Link key={href} href={href}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${active ? "bg-white/10 text-white" : "text-offwhite/70 hover:bg-white/5 hover:text-white"}`}>
            <Icon size={17} className={active ? "text-gold" : ""} />
            <span className="flex-1">{label}</span>
            {badge > 0 && <span className="rounded-full bg-gold px-1.5 text-[11px] font-bold text-navy">{badge}</span>}
          </Link>
        );
      })}
    </nav>
  );
}
