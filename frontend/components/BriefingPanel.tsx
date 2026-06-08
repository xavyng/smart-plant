"use client";

import { Bot, RefreshCw } from "lucide-react";

interface BriefingPanelProps {
  brief: string | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function BriefingPanel({ brief, loading, onRefresh }: BriefingPanelProps) {
  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-accent/15 flex items-center justify-center">
            <Bot size={12} color="#3B82F6" />
          </div>
          <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">AI Briefing</span>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          aria-label="Refresh briefing"
          className="text-slate-600 hover:text-accent transition-colors duration-150 cursor-pointer disabled:opacity-40"
        >
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="p-5 min-h-[90px]">
        {loading ? (
          <div className="space-y-2">
            <div className="h-2.5 bg-border rounded animate-pulse w-full" />
            <div className="h-2.5 bg-border rounded animate-pulse w-5/6" />
            <div className="h-2.5 bg-border rounded animate-pulse w-3/5" />
          </div>
        ) : brief ? (
          <p className="text-slate-400 text-sm leading-relaxed">{brief}</p>
        ) : (
          <p className="text-slate-600 text-sm italic">No briefing available.</p>
        )}
      </div>

      <div className="px-5 py-3 border-t border-border flex items-center gap-2">
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal opacity-50" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-teal" />
        </span>
        <span className="text-slate-600 text-[10px] font-medium">Refreshes every 10s</span>
      </div>
    </div>
  );
}
