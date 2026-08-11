import { LucideIcon } from "lucide-react";

export default function StatCard({
  label,
  value,
  icon: Icon,
  tone = "slate",
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "slate" | "emerald" | "red" | "amber" | "violet" | "blue";
}) {
  const toneClasses: Record<string, string> = {
    slate: "bg-slate-100 text-slate-600",
    emerald: "bg-emerald-100 text-emerald-600",
    red: "bg-red-100 text-red-600",
    amber: "bg-amber-100 text-amber-600",
    violet: "bg-violet-100 text-violet-600",
    blue: "bg-blue-100 text-blue-600",
  };
  return (
    <div className="card p-4 flex items-center gap-3">
      <div className={`rounded-lg p-2.5 ${toneClasses[tone]}`}>
        <Icon size={20} />
      </div>
      <div>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="text-xl font-bold text-slate-900">{value}</div>
      </div>
    </div>
  );
}
