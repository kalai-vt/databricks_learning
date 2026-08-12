import { CheckCircle2, XCircle } from "lucide-react";

const CONFIG: Record<string, { label: string; classes: string; icon: any }> = {
  ALLOW: { label: "ALLOWED", classes: "bg-emerald-100 text-emerald-700", icon: CheckCircle2 },
  BLOCK: { label: "BLOCKED", classes: "bg-red-100 text-red-700", icon: XCircle },
};

const RISK_CLASSES: Record<string, string> = {
  LOW: "bg-slate-100 text-slate-600",
  CRITICAL: "bg-red-100 text-red-700",
};

export function ActionBadge({ action }: { action: string }) {
  const cfg = CONFIG[action] ?? { label: action, classes: "bg-slate-100 text-slate-600", icon: CheckCircle2 };
  const Icon = cfg.icon;
  return (
    <span className={`badge ${cfg.classes}`}>
      <Icon size={13} /> {cfg.label}
    </span>
  );
}

export function RiskBadge({ risk }: { risk: string }) {
  return <span className={`badge ${RISK_CLASSES[risk] ?? "bg-slate-100 text-slate-600"}`}>{risk}</span>;
}

export function ToolBadge({ tool }: { tool: "SQL" | "RAG" | null }) {
  if (!tool) return <span className="badge bg-slate-100 text-slate-400">Tool: none (blocked before agent)</span>;
  const classes = tool === "SQL" ? "bg-blue-100 text-blue-700" : "bg-violet-100 text-violet-700";
  return <span className={`badge ${classes}`}>{tool} Tool</span>;
}
