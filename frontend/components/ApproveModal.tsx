"use client";

import { useState } from "react";
import { X, Send } from "lucide-react";
import { type PendingAction, decideAction } from "@/lib/api";

interface ApproveModalProps {
  action: PendingAction;
  onClose: () => void;
  onSent: () => void;
}

export default function ApproveModal({ action, onClose, onSent }: ApproveModalProps) {
  const p = action.payload as Record<string, unknown>;
  const str = (v: unknown): string => (typeof v === "string" && v ? v : "");

  const [to, setTo] = useState(str(p.recipient));
  const [subject, setSubject] = useState(str(p.subject) || action.action_type);
  const [body, setBody] = useState(
    str(p.body) || str(p.summary) || JSON.stringify(action.payload, null, 2),
  );
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    setLoading(true);
    try {
      await decideAction(action.action_id, "approve", {
        recipient: to,
        subject_override: subject,
        body_override: body,
      });
      onSent();
    } catch {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-lg mx-4 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-white font-semibold">Review &amp; Send</h2>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors duration-150 cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5">To</label>
            <input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="w-full bg-bg border border-border rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full bg-bg border border-border rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5">Body</label>
            <textarea
              rows={8}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full bg-bg border border-border rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-accent resize-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-medium border border-border text-slate-400 hover:text-white transition-all duration-150 cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium bg-success/15 text-success border border-success/25 hover:bg-success/25 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 cursor-pointer"
          >
            <Send size={11} />
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
