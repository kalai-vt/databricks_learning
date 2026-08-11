import { useEffect, useState } from "react";
import { ShieldCheck, ToggleLeft, ToggleRight } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

interface Pillar { pillar: string; implementation: string; status: string; }
interface Policy { policy_code: string; policy_name: string; action: string; enabled: boolean; risk_level: string; }

export default function Governance() {
  const { user } = useAuth();
  const [pillars, setPillars] = useState<Pillar[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [tab, setTab] = useState<"ethical" | "policies">("policies");
  const canToggle = user?.role === "HOSPITAL_ADMIN";

  function load() {
    api.get<{ pillars: Pillar[] }>("/governance/ethical-ai").then((d) => setPillars(d.pillars));
    api.get<{ policies: Policy[] }>("/governance/policies").then((d) => setPolicies(d.policies));
  }

  useEffect(load, []);

  async function toggle(code: string) {
    if (!canToggle) return;
    const updated = await api.post<{ policy_code: string; enabled: boolean }>(`/governance/policies/${code}/toggle`);
    setPolicies((prev) => prev.map((p) => (p.policy_code === code ? { ...p, enabled: updated.enabled } : p)));
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><ShieldCheck size={20} /> Governance</h1>
        <p className="text-sm text-slate-500">Ethical AI pillars and configurable governance policies for {user?.tenant_name ?? "the platform"}.</p>
      </div>

      <div className="flex gap-2">
        <button onClick={() => setTab("policies")} className={`text-sm font-medium px-3 py-1.5 rounded-full ${tab === "policies" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"}`}>Policies</button>
        <button onClick={() => setTab("ethical")} className={`text-sm font-medium px-3 py-1.5 rounded-full ${tab === "ethical" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"}`}>Ethical AI Pillars</button>
      </div>

      {tab === "policies" && (
        <div className="card divide-y divide-slate-100">
          {!canToggle && (
            <div className="p-3 text-xs text-slate-500 bg-slate-50">
              Read-only for your role. Policy changes require Hospital Admin. (Demo mode allows toggling for presentation.)
            </div>
          )}
          {policies.map((p) => (
            <div key={p.policy_code} className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium text-slate-800 text-sm">{p.policy_name}</div>
                <div className="text-xs text-slate-500 font-mono">{p.policy_code} · action: {p.action} · risk: {p.risk_level}</div>
              </div>
              <button onClick={() => toggle(p.policy_code)} disabled={!canToggle} className={!canToggle ? "opacity-50 cursor-not-allowed" : ""}>
                {p.enabled ? <ToggleRight className="text-emerald-500" size={32} /> : <ToggleLeft className="text-slate-300" size={32} />}
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === "ethical" && (
        <div className="grid md:grid-cols-2 gap-4">
          {pillars.map((p) => (
            <div key={p.pillar} className="card p-4">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-slate-800">{p.pillar}</h3>
                <span className="badge bg-emerald-100 text-emerald-700">{p.status}</span>
              </div>
              <p className="text-sm text-slate-500">{p.implementation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
