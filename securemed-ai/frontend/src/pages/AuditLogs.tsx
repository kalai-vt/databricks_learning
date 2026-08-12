import { useEffect, useState } from "react";
import { ScrollText, Search, CheckCircle2, XCircle } from "lucide-react";
import { api } from "../services/api";
import { ActionBadge, RiskBadge, ToolBadge } from "../components/ActionBadge";

interface LogRow {
  id: number; timestamp: string; tenant_code: string; user_name: string; role: string;
  request_text: string | null; policy_code: string | null; risk_level: string | null;
  action: string; model: string | null; tool_used: "SQL" | "RAG" | null;
}

export default function AuditLogs() {
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [riskFilter, setRiskFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (riskFilter) params.set("risk", riskFilter);
    if (actionFilter) params.set("action", actionFilter);
    api.get<{ logs: LogRow[] }>(`/audit/logs?${params.toString()}`).then((d) => setLogs(d.logs));
  }, [riskFilter, actionFilter]);

  const filtered = logs.filter((l) => (l.request_text ?? "").toLowerCase().includes(search.toLowerCase()));
  const allowedCount = logs.filter((l) => l.action === "ALLOW").length;
  const blockedCount = logs.filter((l) => l.action === "BLOCK").length;

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><ScrollText size={20} /> Audit Logging &amp; Monitoring</h1>
        <p className="text-sm text-slate-500">Every AI request — allowed or blocked — is recorded here, including which tool it used and why.</p>
      </div>

      <div className="flex gap-4">
        <div className="card px-4 py-3 flex items-center gap-2 text-sm">
          <ScrollText size={16} className="text-slate-400" /> Total: <strong>{logs.length}</strong>
        </div>
        <div className="card px-4 py-3 flex items-center gap-2 text-sm">
          <CheckCircle2 size={16} className="text-emerald-500" /> Allowed: <strong>{allowedCount}</strong>
        </div>
        <div className="card px-4 py-3 flex items-center gap-2 text-sm">
          <XCircle size={16} className="text-red-500" /> Blocked: <strong>{blockedCount}</strong>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 bg-white border border-slate-300 rounded-lg px-3 py-1.5">
          <Search size={14} className="text-slate-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search request text…" className="text-sm outline-none" />
        </div>
        <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)} className="text-sm border border-slate-300 rounded-lg px-2 py-1.5">
          <option value="">All Risk Levels</option>
          <option value="LOW">Low</option>
          <option value="CRITICAL">Critical</option>
        </select>
        <select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)} className="text-sm border border-slate-300 rounded-lg px-2 py-1.5">
          <option value="">All Actions</option>
          <option value="ALLOW">Allow</option>
          <option value="BLOCK">Block</option>
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
            <tr>
              <th className="text-left p-3">Time</th>
              <th className="text-left p-3">Tenant</th>
              <th className="text-left p-3">User</th>
              <th className="text-left p-3">Request</th>
              <th className="text-left p-3">Tool</th>
              <th className="text-left p-3">Policy</th>
              <th className="text-left p-3">Risk</th>
              <th className="text-left p-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((l) => (
              <tr key={l.id}>
                <td className="p-3 text-xs text-slate-400 whitespace-nowrap">{new Date(l.timestamp).toLocaleString()}</td>
                <td className="p-3 font-mono text-xs">{l.tenant_code}</td>
                <td className="p-3">{l.user_name}</td>
                <td className="p-3 max-w-xs truncate text-slate-600" title={l.request_text ?? ""}>{l.request_text ?? "—"}</td>
                <td className="p-3"><ToolBadge tool={l.tool_used} /></td>
                <td className="p-3 font-mono text-xs">{l.policy_code ?? "—"}</td>
                <td className="p-3">{l.risk_level ? <RiskBadge risk={l.risk_level} /> : "—"}</td>
                <td className="p-3"><ActionBadge action={l.action} /></td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={8} className="p-6 text-center text-slate-400">No audit entries match this filter.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
