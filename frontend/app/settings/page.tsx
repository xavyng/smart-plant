import Sidebar from "@/components/Sidebar";

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 min-w-0 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur-md border-b border-border px-6 py-4">
          <h1 className="text-white text-lg font-semibold">Settings</h1>
          <p className="text-slate-500 text-xs mt-1">Configuration and environment</p>
        </header>

        <div className="p-6 space-y-5">
          {[
            {
              section: "API Connection",
              fields: [
                { label: "Backend URL", value: "http://localhost:8000", note: "Set NEXT_PUBLIC_API_URL to override" },
                { label: "Health endpoint", value: "/health", note: "" },
              ],
            },
            {
              section: "Agent Configuration",
              fields: [
                { label: "Investigator poll interval", value: "60 seconds", note: "" },
                { label: "Action agent poll interval", value: "5 seconds", note: "" },
                { label: "Dashboard refresh interval", value: "10 seconds", note: "" },
              ],
            },
            {
              section: "Shift Schedule",
              fields: [
                { label: "Morning shift", value: "06:00 – 14:00", note: "" },
                { label: "Afternoon shift", value: "14:00 – 22:00", note: "" },
                { label: "Night shift", value: "22:00 – 06:00", note: "" },
              ],
            },
          ].map(({ section, fields }) => (
            <div key={section} className="bg-card border border-border rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-border">
                <h3 className="text-white text-sm font-semibold">{section}</h3>
              </div>
              <div className="divide-y divide-border/50">
                {fields.map(({ label, value, note }) => (
                  <div key={label} className="flex items-center justify-between px-5 py-4">
                    <div>
                      <p className="text-slate-300 text-sm font-medium">{label}</p>
                      {note && <p className="text-slate-600 text-xs mt-0.5">{note}</p>}
                    </div>
                    <span className="text-slate-500 text-sm font-mono bg-surface px-3 py-1 rounded-lg border border-border">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
