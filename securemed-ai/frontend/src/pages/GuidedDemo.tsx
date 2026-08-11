import { useState } from "react";
import { PlayCircle, Loader2 } from "lucide-react";
import { api } from "../services/api";
import { ChatResponse } from "../types";
import { ActionBadge, RiskBadge } from "../components/ActionBadge";
import SecurityTrace from "../components/SecurityTrace";
import { SCENARIOS } from "./AIAssistant";
import { usePresentationMode } from "../hooks/usePresentationMode";

export default function GuidedDemo() {
  const [running, setRunning] = useState<number | null>(null);
  const [result, setResult] = useState<{ scenario: (typeof SCENARIOS)[number]; response: ChatResponse } | null>(null);
  const { presentationMode, togglePresentationMode } = usePresentationMode();

  async function run(idx: number) {
    setRunning(idx);
    try {
      const scenario = SCENARIOS[idx];
      const response = await api.post<ChatResponse>("/ai/chat", { message: scenario.message });
      setResult({ scenario, response });
    } finally {
      setRunning(null);
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2"><PlayCircle size={20} /> Guided Security Demo</h1>
          <p className="text-sm text-slate-500">Click a scenario to execute it live and see the full security decision.</p>
        </div>
        {!presentationMode && (
          <button onClick={togglePresentationMode} className="text-xs font-medium border border-slate-300 rounded-full px-3 py-1.5 hover:bg-slate-100">
            Enter Presentation Mode
          </button>
        )}
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {SCENARIOS.slice(0, 5).map((s, idx) => (
          <button
            key={s.label}
            onClick={() => run(idx)}
            disabled={running !== null}
            className="card p-5 text-left hover:shadow-md hover:border-brand-300 transition-all disabled:opacity-60"
          >
            <div className="text-xs font-semibold text-brand-600 mb-1">{s.label}</div>
            <div className="text-sm text-slate-700 mb-3">"{s.message}"</div>
            <div className="flex items-center justify-between">
              <span className="badge bg-slate-100 text-slate-600">Expected: {s.expected}</span>
              {running === idx && <Loader2 className="animate-spin text-brand-500" size={16} />}
            </div>
          </button>
        ))}
      </div>

      {result && (
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="card p-5">
            <div className="text-xs text-slate-400 mb-1">{result.scenario.label}</div>
            <div className="text-sm text-slate-700 font-medium mb-3">"{result.scenario.message}"</div>
            <div className="flex items-center gap-2 mb-3">
              <ActionBadge action={result.response.action} />
              <RiskBadge risk={result.response.risk_level} />
              <span className="badge bg-slate-100 text-slate-600">{result.response.policy_code}</span>
            </div>
            <div className="text-sm text-slate-600 whitespace-pre-wrap">{result.response.message}</div>
          </div>
          <SecurityTrace steps={result.response.trace} />
        </div>
      )}
    </div>
  );
}
