import { Globe2, Building2 } from "lucide-react";

const TENANT_FEATURES = ["Users", "Roles", "Patient data", "AI conversations", "Policies", "Audit logs", "Usage metrics"];
const PLATFORM_FEATURES = ["AI Gateway", "Governance", "Model Management", "Security Monitoring", "Audit", "Billing", "Tenant Management"];

const USE_CASES: { domain: string; examples: string[] }[] = [
  { domain: "Healthcare (Primary)", examples: ["Hospital AI assistants", "Hospital analytics", "Patient support assistants", "Medical documentation assistance", "Healthcare operations"] },
  { domain: "Banking", examples: ["Customer support", "Fraud analysis", "Employee AI assistants"] },
  { domain: "Insurance", examples: ["Claims processing", "Policy assistants"] },
  { domain: "Education", examples: ["Student assistants", "Institution analytics"] },
  { domain: "HR", examples: ["Recruitment AI", "Employee analytics"] },
  { domain: "Enterprise SaaS", examples: ["CRM AI", "ERP AI", "BI assistants", "Customer support"] },
];

export default function SaaSUseCases() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><Globe2 size={20} /> From Prototype to SaaS</h1>
        <p className="text-sm text-slate-500">How SecureMed AI's architecture scales from two demo tenants to a full multi-tenant SaaS platform.</p>
      </div>

      <div className="card p-6">
        <div className="flex flex-col items-center gap-3">
          <div className="bg-brand-800 text-white font-bold rounded-lg px-4 py-2 text-sm">SecureMed AI Platform</div>
          <div className="w-px h-6 bg-slate-300" />
          <div className="flex gap-6">
            {["H1 Hospital", "H2 Hospital", "H3 Hospital (future)"].map((h) => (
              <div key={h} className="flex flex-col items-center gap-2">
                <div className="w-px h-4 bg-slate-300" />
                <div className="border-2 border-brand-300 bg-brand-50 rounded-lg px-3 py-2 text-xs font-semibold text-brand-800 flex items-center gap-1">
                  <Building2 size={12} /> {h}
                </div>
                <div className="text-[10px] text-slate-400">Tenant</div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-4 mt-6">
          <div className="rounded-lg bg-slate-50 border border-slate-200 p-4">
            <div className="text-xs font-semibold text-slate-600 mb-2">Each tenant gets</div>
            <div className="flex flex-wrap gap-1.5">
              {TENANT_FEATURES.map((f) => <span key={f} className="badge bg-white border border-slate-200 text-slate-600">{f}</span>)}
            </div>
          </div>
          <div className="rounded-lg bg-brand-50 border border-brand-200 p-4">
            <div className="text-xs font-semibold text-brand-700 mb-2">Central platform provides</div>
            <div className="flex flex-wrap gap-1.5">
              {PLATFORM_FEATURES.map((f) => <span key={f} className="badge bg-white border border-brand-200 text-brand-700">{f}</span>)}
            </div>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-base font-bold text-slate-900 mb-1">Potential SaaS Use Cases in India</h2>
        <p className="text-xs text-slate-500 mb-4">
          This prototype is not itself legally compliant. Any production deployment must evaluate applicable Indian
          privacy (DPDP Act), sector-specific, contractual, security, data residency and governance requirements.
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          {USE_CASES.map((u) => (
            <div key={u.domain} className={`card p-4 ${u.domain.startsWith("Healthcare") ? "border-2 border-brand-300" : ""}`}>
              <div className="font-semibold text-slate-800 text-sm mb-2">{u.domain}</div>
              <ul className="text-sm text-slate-500 list-disc list-inside space-y-0.5">
                {u.examples.map((e) => <li key={e}>{e}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
