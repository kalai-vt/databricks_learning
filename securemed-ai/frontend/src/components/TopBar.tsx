import { ShieldCheck, LogOut, Presentation } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePresentationMode } from "../hooks/usePresentationMode";

const ROLE_LABELS: Record<string, string> = {
  SUPER_ADMIN: "Super Admin",
  HOSPITAL_ADMIN: "Hospital Admin",
  DOCTOR: "Doctor",
};

export default function TopBar() {
  const { user, logout } = useAuth();
  const { presentationMode, togglePresentationMode } = usePresentationMode();

  return (
    <header className="bg-brand-900 text-white px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2 font-bold text-lg">
        <ShieldCheck className="text-emerald-400" size={22} />
        SecureMed AI
      </div>

      {user && (
        <div className="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
          <div>
            <span className="text-brand-300">Current Tenant:</span>{" "}
            <span className="font-semibold">{user.tenant_name ?? "Platform (All Tenants)"}</span>
          </div>
          <div>
            <span className="text-brand-300">Current User:</span> <span className="font-semibold">{user.name}</span>
          </div>
          <div>
            <span className="text-brand-300">Role:</span>{" "}
            <span className="font-semibold">{ROLE_LABELS[user.role] ?? user.role}</span>
          </div>
          <div className="badge bg-emerald-500/20 text-emerald-300">
            <ShieldCheck size={13} /> PROTECTED
          </div>
          <div className="badge bg-amber-500/20 text-amber-300">Demo Mode: ON</div>
          <button
            onClick={togglePresentationMode}
            className={`badge ${presentationMode ? "bg-white text-brand-900" : "bg-brand-700 text-white"} hover:opacity-90`}
            title="Toggle Presentation Mode"
          >
            <Presentation size={13} /> Presentation
          </button>
          <button onClick={logout} className="badge bg-red-500/20 text-red-300 hover:bg-red-500/30" title="Log out">
            <LogOut size={13} /> Logout
          </button>
        </div>
      )}
    </header>
  );
}
