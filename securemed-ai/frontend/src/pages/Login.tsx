import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, AlertTriangle, Loader2 } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";

const DEMO_EMAIL = "arun@h1.demo";
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
      navigate("/assistant");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  function useDemo() {
    setEmail(DEMO_EMAIL);
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
        <div className="w-full max-w-sm">
          <div className="card p-8">
            <div className="flex items-center gap-2 text-brand-700 mb-1">
              <ShieldCheck size={28} />
              <h1 className="text-2xl font-bold text-slate-900">SecureMed AI</h1>
            </div>
            <p className="text-sm text-slate-500 mb-6">Multi-Tenant Isolation Security Demo</p>

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

            <button
              onClick={useDemo}
              className="w-full text-left mt-5 border border-slate-200 rounded-lg p-3 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 text-sm">H1 Hospital — Dr. Arun</span>
                <span className="badge bg-slate-100 text-slate-600">Doctor</span>
              </div>
              <div className="text-xs text-slate-500 mt-1 font-mono">{DEMO_EMAIL}</div>
              <div className="text-xs text-slate-400 font-mono">Password: {DEMO_PASSWORD}</div>
            </button>

            <p className="text-xs text-slate-400 mt-4">
              Demo credentials only. Passwords are stored using bcrypt hashing — never in plaintext.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
