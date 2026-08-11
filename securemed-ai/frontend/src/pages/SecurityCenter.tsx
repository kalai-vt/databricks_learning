import { useEffect, useState } from "react";
import { Radar, ShieldAlert } from "lucide-react";
import { api } from "../services/api";
import { RiskBadge } from "../components/ActionBadge";

interface SecEvent {
  id: number; timestamp: string; tenant_code: string; tenant_name: string; user_name: string;
  event_type: string; severity: string; action: string; description: string;
}

const CONTROLS = [
  { group: "Authentication", items: ["JWT-based sessions", "Bcrypt password hashing"] },
  { group: "Authorization", items: ["Role-Based Access Control (RBAC)", "Server-side authorization on every route"] },
  { group: "Tenant Isolation", items: ["Server-side tenant context (from JWT only)", "Tenant-scoped database queries", "Cross-tenant request blocking"] },
  { group: "Data Protection", items: ["PII/PHI detection", "Field-level masking", "Data minimization before LLM calls"] },
  { group: "AI Security", items: ["Prompt injection detection", "Response validation", "No secrets ever placed in prompts"] },
  { group: "Governance", items: ["Policy engine", "Risk scoring", "Mandatory human review for high-risk requests", "Full audit logging"] },
];

export default function SecurityCenter() {
  const [events, setEvents] = useState<SecEvent[]>([]);

  useEffect(() => {
    api.get<{ events: SecEvent[] }>("/security/events").then((d) => setEvents(d.events));
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><Radar size={20} /> Security Center</h1>
        <p className="text-sm text-slate-500">Live feed of security-relevant events: cross-tenant attempts, prompt injection, PII detection, and more.</p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
            <tr>
              <th className="text-left p-3">Time</th>
              <th className="text-left p-3">Severity</th>
              <th className="text-left p-3">Type</th>
              <th className="text-left p-3">Tenant</th>
              <th className="text-left p-3">User</th>
              <th className="text-left p-3">Action</th>
              <th className="text-left p-3">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {events.map((e) => (
              <tr key={e.id} className={e.severity === "CRITICAL" ? "bg-red-50/50" : ""}>
                <td className="p-3 text-xs text-slate-400 whitespace-nowrap">{new Date(e.timestamp).toLocaleString()}</td>
                <td className="p-3"><RiskBadge risk={e.severity} /></td>
                <td className="p-3 flex items-center gap-1.5"><ShieldAlert size={14} className="text-slate-400" /> {e.event_type.replace(/_/g, " ")}</td>
                <td className="p-3 font-mono text-xs">{e.tenant_code}</td>
                <td className="p-3">{e.user_name}</td>
                <td className="p-3"><span className="badge bg-slate-100 text-slate-600">{e.action}</span></td>
                <td className="p-3 text-slate-500 max-w-md">{e.description}</td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr><td colSpan={7} className="p-6 text-center text-slate-400">No security events yet — try the Guided Demo.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-2">Security Controls</h2>
        <div className="grid md:grid-cols-3 gap-3">
          {CONTROLS.map((c) => (
            <div key={c.group} className="card p-4">
              <div className="font-medium text-slate-800 text-sm mb-2">{c.group}</div>
              <ul className="space-y-1 text-xs text-slate-500">
                {c.items.map((i) => <li key={i}>✓ {i}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
