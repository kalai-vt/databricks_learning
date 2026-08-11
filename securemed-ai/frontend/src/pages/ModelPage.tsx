import { useEffect, useState } from "react";
import { Cpu, Network } from "lucide-react";
import { api } from "../services/api";

interface ModelConfig {
  provider: string; model: string; status: string; mock_mode: boolean; architecture: string;
  why_this_model: string[]; positioning_statement: string; future_models: string[]; evaluation_criteria: string[]; note: string;
}

export default function ModelPage() {
  const [cfg, setCfg] = useState<ModelConfig | null>(null);

  useEffect(() => {
    api.get<ModelConfig>("/model/config").then(setCfg);
  }, []);

  if (!cfg) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><Cpu size={20} /> LLM Configuration</h1>
      </div>

      <div className="card p-5 grid sm:grid-cols-3 gap-4">
        <div>
          <div className="text-xs text-slate-500">Current Provider</div>
          <div className="text-lg font-bold text-slate-900">{cfg.provider}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Current Model</div>
          <div className="text-lg font-bold text-slate-900">{cfg.model}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Status</div>
          <div className="text-lg font-bold text-emerald-600">
            {cfg.status} {cfg.mock_mode && <span className="text-amber-600 text-sm">(DEMO / MOCK MODE)</span>}
          </div>
        </div>
      </div>

      <div className="card p-5">
        <h2 className="font-semibold text-slate-800 mb-2">Why GPT-4o-mini for the prototype?</h2>
        <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-1 text-sm text-slate-600 list-disc list-inside">
          {cfg.why_this_model.map((r) => <li key={r}>{r}</li>)}
        </ul>
        <p className="text-sm text-slate-500 mt-4 italic border-l-4 border-brand-300 pl-3">{cfg.positioning_statement}</p>
      </div>

      <div className="card p-5">
        <h2 className="font-semibold text-slate-800 mb-3 flex items-center gap-2"><Network size={16} /> Future Model Evaluation</h2>
        <p className="text-sm text-slate-500 mb-3">Models that can be evaluated later: {cfg.future_models.join(", ")}.</p>
        <div className="text-xs text-slate-500 mb-3">Evaluation criteria: {cfg.evaluation_criteria.join(" · ")}</div>

        <pre className="bg-slate-900 text-emerald-300 text-xs rounded-lg p-4 overflow-x-auto">
{`Governance Gateway
   |
   +-- GPT-4o-mini   (active)
   +-- Claude
   +-- Gemini
   +-- Local / Open-Source Model`}
        </pre>
        <p className="text-sm font-medium text-brand-700 mt-3">{cfg.note}</p>
      </div>
    </div>
  );
}
