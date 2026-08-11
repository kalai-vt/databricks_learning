import { useState } from "react";
import { Network, ArrowDown, XCircle, CheckCircle2 } from "lucide-react";

interface Component {
  id: string;
  label: string;
  purpose: string;
  security_function: string;
  implementation: string;
  threat_prevented: string;
}

const PIPELINE: Component[] = [
  { id: "auth", label: "Authentication / JWT", purpose: "Confirm the caller is a known, active user.", security_function: "Identity verification", implementation: "Bcrypt password hashing + signed JWT session tokens", threat_prevented: "Anonymous / unauthenticated access" },
  { id: "tenant", label: "Tenant Context", purpose: "Derive which hospital this request belongs to.", security_function: "Server-side tenant binding", implementation: "tenant_code embedded in JWT at login, read-only afterwards", threat_prevented: "Client-supplied tenant_id spoofing" },
  { id: "rbac", label: "RBAC", purpose: "Confirm the user's role permits this action.", security_function: "Authorization", implementation: "Role dependency checks on every route (Doctor / Hospital Admin / Super Admin)", threat_prevented: "Privilege escalation" },
  { id: "pii", label: "PII/PHI Detection", purpose: "Detect requests for sensitive patient fields.", security_function: "Data minimization", implementation: "Keyword + patient-record matching, field-level masking", threat_prevented: "Sensitive data leakage to LLM/user" },
  { id: "injection", label: "Prompt Injection Detection", purpose: "Detect attempts to override system instructions.", security_function: "Input security", implementation: "Deterministic pattern matching before the LLM is ever called", threat_prevented: "Jailbreaks, secret exfiltration" },
  { id: "risk", label: "Risk Classification", purpose: "Classify request severity.", security_function: "Risk-based governance", implementation: "Keyword-based high-risk healthcare detection", threat_prevented: "Unsupervised medical decisions" },
  { id: "policy", label: "Policy Engine", purpose: "Apply the tenant's configured governance policies.", security_function: "Governance", implementation: "Per-tenant, toggleable policy table (ai_policies)", threat_prevented: "Inconsistent or missing enforcement" },
  { id: "isolation", label: "Tenant Isolation", purpose: "Block any cross-tenant reference.", security_function: "Multi-tenant security", implementation: "Tenant-code mention detection + tenant-scoped queries", threat_prevented: "Cross-tenant data access" },
  { id: "db", label: "Tenant-Scoped Database", purpose: "Retrieve only this tenant's data.", security_function: "Data isolation", implementation: "WHERE tenant_id = authenticated_tenant_id on every query", threat_prevented: "Accidental or malicious cross-tenant reads" },
  { id: "llm", label: "LLM Provider", purpose: "Generate a natural-language answer.", security_function: "Model-agnostic generation", implementation: "LLMProvider interface -> OpenAIProvider (GPT-4o-mini)", threat_prevented: "Vendor lock-in; LLM never decides authorization" },
  { id: "validate", label: "Response Validation", purpose: "Re-check LLM output before it reaches the user.", security_function: "Output security", implementation: "Regex re-scan for emails/phone numbers before display", threat_prevented: "PII leakage via model output" },
  { id: "audit", label: "Audit Log", purpose: "Record every decision.", security_function: "Accountability", implementation: "audit_logs + security_events tables for every ALLOW/BLOCK/MASK/HUMAN_REVIEW", threat_prevented: "Undetected misuse; no forensic trail" },
];

export default function Architecture() {
  const [selected, setSelected] = useState<Component>(PIPELINE[0]);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><Network size={20} /> Architecture</h1>
        <p className="text-sm text-slate-500">
          Core principle: <strong>security must not depend on the LLM.</strong> Click any stage to see its security function.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-4">
          <div className="flex flex-col items-center gap-1">
            <PipelineNode label="USER" />
            <ArrowDown size={16} className="text-slate-300" />
            {PIPELINE.map((c, i) => (
              <div key={c.id} className="flex flex-col items-center gap-1 w-full">
                <button
                  onClick={() => setSelected(c)}
                  className={`w-full max-w-md text-sm font-medium rounded-lg border px-3 py-2 transition-colors ${
                    selected.id === c.id ? "border-brand-500 bg-brand-50 text-brand-800" : "border-slate-200 hover:bg-slate-50 text-slate-700"
                  }`}
                >
                  {c.label}
                </button>
                {i < PIPELINE.length - 1 && <ArrowDown size={16} className="text-slate-300" />}
              </div>
            ))}
            <ArrowDown size={16} className="text-slate-300" />
            <PipelineNode label="USER" />
          </div>
        </div>

        <div className="card p-4 h-fit sticky top-4">
          <h3 className="font-semibold text-slate-800 mb-3">{selected.label}</h3>
          <dl className="space-y-3 text-sm">
            <div><dt className="text-xs uppercase text-slate-400">Purpose</dt><dd className="text-slate-600">{selected.purpose}</dd></div>
            <div><dt className="text-xs uppercase text-slate-400">Security Function</dt><dd className="text-slate-600">{selected.security_function}</dd></div>
            <div><dt className="text-xs uppercase text-slate-400">Implementation</dt><dd className="text-slate-600">{selected.implementation}</dd></div>
            <div><dt className="text-xs uppercase text-slate-400">Threat Prevented</dt><dd className="text-slate-600">{selected.threat_prevented}</dd></div>
          </dl>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-4 border-2 border-red-200">
          <h3 className="font-semibold text-red-700 flex items-center gap-2 mb-3"><XCircle size={16} /> BAD APPROACH</h3>
          <div className="flex flex-col items-center gap-2 text-sm">
            <Node text="User Prompt" tone="red" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="tenant_id read from prompt" tone="red" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Database" tone="red" />
          </div>
          <p className="text-xs text-red-600 mt-3 italic">Never trust tenant identity supplied by the user.</p>
        </div>

        <div className="card p-4 border-2 border-emerald-200">
          <h3 className="font-semibold text-emerald-700 flex items-center gap-2 mb-3"><CheckCircle2 size={16} /> SECURE APPROACH</h3>
          <div className="flex flex-col items-center gap-2 text-sm">
            <Node text="Authenticated User" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="JWT" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Server-side Tenant Context" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Authorization" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Tenant-scoped Query" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Database" tone="emerald" />
          </div>
        </div>
      </div>
    </div>
  );
}

function PipelineNode({ label }: { label: string }) {
  return <div className="bg-slate-800 text-white text-xs font-bold rounded-full px-4 py-1.5">{label}</div>;
}

function Node({ text, tone }: { text: string; tone: "red" | "emerald" }) {
  const classes = tone === "red" ? "border-red-300 bg-red-50 text-red-700" : "border-emerald-300 bg-emerald-50 text-emerald-700";
  return <div className={`border rounded-lg px-3 py-1.5 w-full text-center ${classes}`}>{text}</div>;
}
