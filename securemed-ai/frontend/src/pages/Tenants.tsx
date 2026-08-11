import { useEffect, useState } from "react";
import { Building2, Lock, ShieldCheck, Users, Activity, Radar } from "lucide-react";
import { api } from "../services/api";

interface TenantRow {
  tenant_code: string;
  tenant_name: string;
  location: string;
  status: string;
  accessible: boolean;
  users?: number;
  patients?: number;
  ai_requests?: number;
  security_events?: number;
  reason?: string;
}

export default function Tenants() {
  const [tenants, setTenants] = useState<TenantRow[]>([]);

  useEffect(() => {
    api.get<{ tenants: TenantRow[] }>("/tenants").then((d) => setTenants(d.tenants));
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><Building2 size={20} /> Tenants</h1>
        <p className="text-sm text-slate-500">
          Each hospital is a fully isolated tenant on a shared platform. Data never crosses tenant boundaries.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {tenants.map((t) => (
          <div
            key={t.tenant_code}
            className={`card p-5 border-2 ${t.accessible ? "border-emerald-200" : "border-slate-200 bg-slate-50"}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-brand-100 text-brand-700 px-2 py-1 font-mono text-xs font-bold">
                  {t.tenant_code}
                </div>
                <h2 className="font-semibold text-slate-900">{t.tenant_name}</h2>
              </div>
              <span className="badge bg-emerald-100 text-emerald-700">
                <ShieldCheck size={12} /> {t.status}
              </span>
            </div>
            <div className="text-sm text-slate-500 mb-3">Location: {t.location}</div>

            {t.accessible ? (
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2"><Users size={14} className="text-slate-400" /> Users: <strong>{t.users}</strong></div>
                <div className="flex items-center gap-2"><Users size={14} className="text-slate-400" /> Patients: <strong>{t.patients}+</strong></div>
                <div className="flex items-center gap-2"><Activity size={14} className="text-slate-400" /> AI Requests: <strong>{t.ai_requests}</strong></div>
                <div className="flex items-center gap-2"><Radar size={14} className="text-slate-400" /> Security Events: <strong>{t.security_events}</strong></div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-slate-500 bg-white border border-slate-200 rounded-lg p-3">
                <Lock size={16} className="text-red-400" />
                <span>{t.reason ?? "Cross-tenant access blocked"}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
