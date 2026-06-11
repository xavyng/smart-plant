"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  GitBranch,
  Bot,
  Settings,
  CheckCircle2,
} from "lucide-react";
import { getPendingActions } from "@/lib/api";

const NAV = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/pipeline", icon: GitBranch, label: "Pipeline" },
  { href: "/agents", icon: Bot, label: "Agents" },
  { href: "/approvals", icon: CheckCircle2, label: "Approvals" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    getPendingActions()
      .then((a) => setPendingCount(a.length))
      .catch(() => {});
  }, []);

  return (
    <aside className="hidden md:flex w-56 min-h-screen flex-col bg-surface border-r border-border shrink-0">
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent/15 border border-accent/25 flex items-center justify-center shrink-0">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22V12" />
              <path d="M12 12C10 8 6 7 4 8c0 4 4 6 8 4z" />
              <path d="M12 12C14 8 18 7 20 8c0 4-4 6-8 4z" />
            </svg>
          </div>
          <div>
            <p className="text-white text-sm font-semibold leading-none tracking-tight">
              Smart Plant
            </p>
            <p className="text-slate-500 text-[11px] mt-0.5">Factory Monitor</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 ${
                active
                  ? "bg-accent/12 text-accent"
                  : "text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]"
              }`}
            >
              <Icon size={15} strokeWidth={active ? 2.5 : 1.75} />
              <span className="text-sm font-medium">{label}</span>
              {label === "Approvals" && pendingCount > 0 ? (
                <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-warning/20 text-warning">
                  {pendingCount}
                </span>
              ) : active ? (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-accent" />
              ) : null}
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 border-t border-border">
        <p className="text-slate-600 text-xs">v1.0.0 · Production</p>
      </div>
    </aside>
  );
}
