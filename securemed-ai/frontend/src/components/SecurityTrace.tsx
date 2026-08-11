import { CheckCircle2, XCircle, MinusCircle } from "lucide-react";
import { TraceStep } from "../types";

function iconFor(status: string) {
  if (status === "PASS" || status.match(/ALLOW|MASK|HUMAN_REVIEW/)) return <CheckCircle2 className="text-emerald-500" size={18} />;
  if (status === "FAIL" || status === "BLOCKED") return <XCircle className="text-red-500" size={18} />;
  return <MinusCircle className="text-slate-300" size={18} />;
}

export default function SecurityTrace({ steps }: { steps: TraceStep[] }) {
  return (
    <div className="card p-4">
      <h3 className="font-semibold text-slate-800 mb-3 text-sm">Security Execution Trace</h3>
      <ol className="space-y-2">
        {steps.map((s) => (
          <li key={s.step} className="flex items-start gap-3 text-sm">
            <span className="mt-0.5">{iconFor(s.status)}</span>
            <div>
              <div className="font-medium text-slate-700">
                {s.step}. {s.label}{" "}
                <span className="text-xs font-mono text-slate-400 ml-1">[{s.status}]</span>
              </div>
              <div className="text-xs text-slate-500">{s.detail}</div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
