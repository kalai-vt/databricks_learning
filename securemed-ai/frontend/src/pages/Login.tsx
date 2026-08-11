import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, AlertTriangle, Loader2 } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";

const DEMO_CREDENTIALS = [
  { org: "H1 Hospital", email: "arun@h1.demo", role: "Doctor", color: "bg-blue-50 border-blue-200" },
  { org: "H2 Hospital", email: "meera@h2.demo", role: "Doctor", color: "bg-purple-50 border-purple-200" },
  { org: "H1 Admin", email: "priya@h1.demo", role: "Hospital Admin", color: "bg-emerald-50 border-emerald-200" },
  { org: "Platform Admin", email: "admin@securemed.demo", role: "Super Admin", color: "bg-amber-50 border-amber-200" },
];

const DEMO_PASSWORD = "Demo@123";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/overview");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  function useDemo(demoEmail: string) {
    setEmail(demoEmail);
    setPassword(DEMO_PASSWORD);
    setError(null);
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-brand-900 via-brand-800 to-slate-900">
      <div className="bg-amber-500 text-amber-950 text-center text-xs sm:text-sm font-semibold py-1.5 px-3 flex items-center justify-center gap-2">
        <AlertTriangle size={14} className="shrink-0" />
        DEMO ENVIRONMENT — SYNTHETIC HEALTHCARE DATA — NOT FOR MEDICAL USE
      </div>

      <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-4xl grid md:grid-cols-2 gap-6 items-start">
          <div className="card p-8 order-2 md:order-1">
            <div className="flex items-center gap-2 text-brand-700 mb-1">
              <ShieldCheck size={28} />
              <h1 className="text-2xl font-bold text-slate-900">SecureMed AI</h1>
            </div>
            <p className="text-sm text-slate-500 mb-6">Ethical AI &amp; Multi-Tenant Security Governance</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@hospital.demo"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {error && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-semibold rounded-lg py-2.5 text-sm transition-colors"
              >
                {loading && <Loader2 className="animate-spin" size={16} />}
                Sign In
              </button>
            </form>

            <p className="text-xs text-slate-400 mt-6">
              These are demo credentials only, for a synthetic-data security governance demonstration.
              Passwords are stored using bcrypt hashing — never in plaintext.
            </p>
          </div>

          <div className="order-1 md:order-2 space-y-3">
            <p className="text-white/80 text-sm font-medium px-1">Demo credentials — click a card to autofill:</p>
            {DEMO_CREDENTIALS.map((c) => (
              <button
                key={c.email}
                onClick={() => useDemo(c.email)}
                className={`w-full text-left card ${c.color} p-4 hover:shadow-md transition-shadow`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-800">{c.org}</span>
                  <span className="badge bg-slate-900/5 text-slate-600">{c.role}</span>
                </div>
                <div className="text-xs text-slate-500 mt-1 font-mono">{c.email}</div>
                <div className="text-xs text-slate-400 font-mono">Password: {DEMO_PASSWORD}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
