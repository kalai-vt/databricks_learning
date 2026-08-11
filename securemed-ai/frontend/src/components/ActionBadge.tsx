import { CheckCircle2, XCircle, EyeOff, UserCheck } from "lucide-react";

const CONFIG: Record<string, { label: string; classes: string; icon: any }> = {
  ALLOW: { label: "ALLOWED", classes: "bg-emerald-100 text-emerald-700", icon: CheckCircle2 },
  BLOCK: { label: "BLOCKED", classes: "bg-red-100 text-red-700", icon: XCircle },
  MASK: { label: "MASKED", classes: "bg-amber-100 text-amber-700", icon: EyeOff },
  HUMAN_REVIEW: { label: "HUMAN REVIEW", classes: "bg-violet-100 text-violet-700", icon: UserCheck },
};

const RISK_CLASSES: Record<string, string> = {
  LOW: "bg-slate-100 text-slate-600",
  MEDIUM: "bg-amber-100 text-amber-700",
  HIGH: "bg-orange-100 text-orange-700",
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
