import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend } from "recharts";
import { MessageSquareText, CheckCircle2, XCircle, EyeOff, Radar, Users, ShieldCheck } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import StatCard from "../components/StatCard";

interface OverviewStats {
  current_tenant: string | null;
  cards: {
    ai_requests: number; allowed: number; blocked: number; pii_protected: number;
    human_review: number; security_events: number; cross_tenant_attempts: number;
  };
  charts: {
    requests_by_status: { name: string; value: number }[];
    security_events_by_type: { name: string; value: number }[];
    tenant_activity: { tenant_code: string; tenant_name: string; ai_requests: number }[];
    policy_violations: { name: string; value: number }[];
  };
  governance_active: Record<string, boolean>;
}

const COLORS = ["#2563eb", "#ef4444", "#f59e0b", "#8b5cf6", "#10b981", "#0ea5e9"];

const GOVERNANCE_LABELS: Record<string, string> = {
  authentication: "Authentication",
  rbac: "RBAC",
  tenant_isolation: "Tenant Isolation",
  pii_protection: "PII Protection",
  prompt_security: "Prompt Security",
  audit_logging: "Audit Logging",
  response_validation: "Response Validation",
};

export default function Overview() {
  const { user } = useAuth();
  const [stats, setStats] = useState<OverviewStats | null>(null);

  useEffect(() => {
    api.get<OverviewStats>("/overview/stats").then(setStats).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="card p-5 bg-gradient-to-r from-brand-700 to-brand-900 text-white">
        <p className="text-lg font-semibold leading-snug">
          "AI should not only be intelligent. It should be governed, secure, privacy-aware, auditable, and
          tenant-isolated."
        </p>
        <p className="text-sm text-brand-100 mt-2">
          SecureMed AI demonstrates how a shared healthcare SaaS platform can safely provide AI capabilities to
          multiple hospitals without allowing cross-tenant data access.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Current Tenant" value={user?.tenant_name ?? "Platform"} icon={Users} tone="blue" />
        <StatCard label="AI Requests" value={stats?.cards.ai_requests ?? "—"} icon={MessageSquareText} tone="slate" />
        <StatCard label="Allowed" value={stats?.cards.allowed ?? "—"} icon={CheckCircle2} tone="emerald" />
        <StatCard label="Blocked" value={stats?.cards.blocked ?? "—"} icon={XCircle} tone="red" />
        <StatCard label="PII Protected" value={stats?.cards.pii_protected ?? "—"} icon={EyeOff} tone="amber" />
        <StatCard label="Human Review" value={stats?.cards.human_review ?? "—"} icon={ShieldCheck} tone="violet" />
        <StatCard label="Security Events" value={stats?.cards.security_events ?? "—"} icon={Radar} tone="red" />
        <StatCard label="Cross-Tenant Attempts" value={stats?.cards.cross_tenant_attempts ?? "—"} icon={XCircle} tone="red" />
      </div>

      <div className="card p-5 flex items-center gap-3 border-2 border-emerald-300 bg-emerald-50">
        <ShieldCheck className="text-emerald-600" size={28} />
        <div>
          <div className="text-lg font-bold text-emerald-800">AI GOVERNANCE ACTIVE</div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm text-emerald-700">
            {stats &&
              Object.entries(stats.governance_active).map(([k, v]) => (
                <span key={k}>{v ? "✓" : "✗"} {GOVERNANCE_LABELS[k] ?? k}</span>
              ))}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-4">
          <h3 className="font-semibold text-slate-700 text-sm mb-3">Requests by Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={stats?.charts.requests_by_status ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-4">
          <h3 className="font-semibold text-slate-700 text-sm mb-3">Security Events by Type</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={stats?.charts.security_events_by_type ?? []}
                dataKey="value"
                nameKey="name"
                outerRadius={80}
                label={(d) => d.name}
              >
                {(stats?.charts.security_events_by_type ?? []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-4">
          <h3 className="font-semibold text-slate-700 text-sm mb-3">Tenant Activity</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={stats?.charts.tenant_activity ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="tenant_code" fontSize={12} />
              <YAxis fontSize={12} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="ai_requests" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-4">
          <h3 className="font-semibold text-slate-700 text-sm mb-3">Policy Violations</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={stats?.charts.policy_violations ?? []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" fontSize={12} allowDecimals={false} />
              <YAxis type="category" dataKey="name" fontSize={11} width={140} />
              <Tooltip />
              <Bar dataKey="value" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
