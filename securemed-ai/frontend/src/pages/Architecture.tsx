import { useEffect, useState } from "react";
import { Network, ArrowDown, XCircle, CheckCircle2, Building2, Lock, ShieldCheck } from "lucide-react";
import { api } from "../services/api";

interface Component {
  id: string;
  label: string;
  purpose: string;
  security_function: string;
  implementation: string;
  threat_prevented: string;
}

const LINEAR_STAGES: Component[] = [
  { id: "auth", label: "Authentication (JWT / OAuth)", purpose: "Confirm the caller is a known, active user.", security_function: "Identity verification", implementation: "Bcrypt password hashing + signed JWT session tokens", threat_prevented: "Anonymous / unauthenticated access" },
  { id: "tenant", label: "Tenant Context (H1 / H2)", purpose: "Derive which hospital this request belongs to.", security_function: "Server-side tenant binding", implementation: "tenant_code embedded in JWT at login, read-only afterwards — never re-derived from the prompt", threat_prevented: "Client- or prompt-supplied tenant_id spoofing" },
  { id: "authz", label: "Authorization (RBAC + RLS)", purpose: "Confirm the user's role permits this action, and pin every downstream query to their tenant.", security_function: "Access control", implementation: "Role dependency checks on every route + tenant_id captured for use as a Row-Level Security predicate", threat_prevented: "Privilege escalation and missing tenant filters" },
  { id: "agent", label: "LLM / Agent", purpose: "Interpret the request and decide which tool can answer it.", security_function: "Orchestration only — never authorization", implementation: "LLMProvider abstraction (GPT-4o-mini via OpenAI today); the agent picks a tool, it does not pick a tenant", threat_prevented: "LLM being trusted as a security boundary" },
];

const TOOL_BRANCHES = {
  sql: {
    id: "sql", label: "SQL Tool", filterLabel: "RLS Filter", storeLabel: "Database",
    purpose: "Answer structured/statistical questions (counts, admissions).",
    security_function: "Row-Level Security enforcement",
    implementation: "SELECT ... FROM patients WHERE tenant_id = authenticated_tenant_id — filter applied server-side, before the query runs",
    threat_prevented: "Cross-tenant row leakage via a manipulated prompt",
  },
  rag: {
    id: "rag", label: "RAG Tool", filterLabel: "Tenant Filter", storeLabel: "Vector Database",
    purpose: "Answer knowledge/policy questions from hospital documents.",
    security_function: "Tenant-namespaced retrieval",
    implementation: "Similarity search runs only over documents WHERE tenant_id = authenticated_tenant_id, before ranking",
    threat_prevented: "Cross-tenant document leakage through semantic search",
  },
};

const FINAL_STAGE: Component = {
  id: "audit", label: "Audit Logging", purpose: "Record every decision, allowed or blocked.", security_function: "Accountability", implementation: "Every request writes an audit_logs row: tenant, user, tool used, action, risk, policy", threat_prevented: "Undetected misuse; no forensic trail",
};

interface TenantRow {
  tenant_code: string; tenant_name: string; location: string; status: string; accessible: boolean;
  patients?: number; documents?: number; reason?: string;
}

export default function Architecture() {
  const [selected, setSelected] = useState<Component>(LINEAR_STAGES[0]);
  const [tenants, setTenants] = useState<TenantRow[]>([]);

  useEffect(() => {
    api.get<{ tenants: TenantRow[] }>("/tenants").then((d) => setTenants(d.tenants)).catch(() => {});
  }, []);

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
            <PipelineNode label="USER / UI" />
            <ArrowDown size={16} className="text-slate-300" />
            {LINEAR_STAGES.map((c) => (
              <div key={c.id} className="flex flex-col items-center gap-1 w-full">
                <StageButton c={c} selected={selected} onSelect={setSelected} />
                <ArrowDown size={16} className="text-slate-300" />
              </div>
            ))}

            <div className="grid grid-cols-2 gap-4 w-full max-w-lg">
              {(["sql", "rag"] as const).map((key) => {
                const tool = TOOL_BRANCHES[key];
                const filterNode: Component = { id: `${key}-filter`, label: tool.filterLabel, purpose: `Enforce tenant scope for the ${tool.label}.`, security_function: tool.security_function, implementation: tool.implementation, threat_prevented: tool.threat_prevented };
                const storeNode: Component = { id: `${key}-store`, label: tool.storeLabel, purpose: `Where ${tool.label} results physically live, already tenant-partitioned.`, security_function: "Data isolation at rest", implementation: key === "sql" ? "Single tenant-scoped SQL table, filtered before every read" : "Documents tagged with tenant_id; queried as a per-tenant namespace", threat_prevented: "Direct cross-tenant reads" };
                return (
                  <div key={key} className="flex flex-col items-center gap-1">
                    <StageButton c={{ id: tool.id, label: tool.label, purpose: `See: ${tool.label} above.`, security_function: tool.security_function, implementation: tool.implementation, threat_prevented: tool.threat_prevented }} selected={selected} onSelect={setSelected} />
                    <ArrowDown size={14} className="text-slate-300" />
                    <StageButton c={filterNode} selected={selected} onSelect={setSelected} small />
                    <ArrowDown size={14} className="text-slate-300" />
                    <StageButton c={storeNode} selected={selected} onSelect={setSelected} small />
                  </div>
                );
              })}
            </div>

            <ArrowDown size={16} className="text-slate-300" />
            <StageButton c={FINAL_STAGE} selected={selected} onSelect={setSelected} />
            <ArrowDown size={16} className="text-slate-300" />
            <PipelineNode label="USER / UI" />
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
            <Node text="SQL / Vector Database" tone="red" />
          </div>
          <p className="text-xs text-red-600 mt-3 italic">Never trust tenant identity supplied by the user or the LLM.</p>
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
            <Node text="Authorization (RBAC + RLS)" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="Tenant-scoped Tool Call (SQL / RAG)" tone="emerald" />
            <ArrowDown size={14} className="text-slate-300" />
            <Node text="SQL / Vector Database" tone="emerald" />
          </div>
        </div>
      </div>

      <div className="card p-5">
        <h3 className="font-semibold text-slate-800 mb-1 flex items-center gap-2"><ShieldCheck size={16} className="text-emerald-600" /> Live Tenant Isolation Proof</h3>
        <p className="text-xs text-slate-500 mb-4">Logged in as an H1 user, this is exactly what the API returns for /api/tenants — H1 is fully visible, H2 is protected.</p>
        <div className="grid md:grid-cols-2 gap-4">
          {tenants.map((t) => (
            <div key={t.tenant_code} className={`rounded-lg border-2 p-4 ${t.accessible ? "border-emerald-200 bg-emerald-50/50" : "border-slate-200 bg-slate-50"}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 font-semibold text-slate-800">
                  <Building2 size={14} /> {t.tenant_name} <span className="text-xs font-mono text-slate-400">({t.tenant_code})</span>
                </div>
                <span className={`badge ${t.accessible ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-500"}`}>{t.status}</span>
              </div>
              {t.accessible ? (
                <div className="text-sm text-slate-600 flex gap-4">
                  <span>Patients: <strong>{t.patients}</strong></span>
                  <span>Documents: <strong>{t.documents}</strong></span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Lock size={14} className="text-red-400" /> {t.reason ?? "Cross-tenant access blocked"}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PipelineNode({ label }: { label: string }) {
  return <div className="bg-slate-800 text-white text-xs font-bold rounded-full px-4 py-1.5">{label}</div>;
}

function StageButton({ c, selected, onSelect, small }: { c: Component; selected: Component; onSelect: (c: Component) => void; small?: boolean }) {
  return (
    <button
      onClick={() => onSelect(c)}
      className={`w-full ${small ? "max-w-[220px] text-xs py-1.5" : "max-w-md text-sm py-2"} font-medium rounded-lg border px-3 transition-colors ${
        selected.id === c.id ? "border-brand-500 bg-brand-50 text-brand-800" : "border-slate-200 hover:bg-slate-50 text-slate-700"
      }`}
    >
      {c.label}
    </button>
  );
}

function Node({ text, tone }: { text: string; tone: "red" | "emerald" }) {
  const classes = tone === "red" ? "border-red-300 bg-red-50 text-red-700" : "border-emerald-300 bg-emerald-50 text-emerald-700";
  return <div className={`border rounded-lg px-3 py-1.5 w-full text-center ${classes}`}>{text}</div>;
}
