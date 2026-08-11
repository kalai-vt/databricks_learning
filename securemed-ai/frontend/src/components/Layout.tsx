import { Outlet, Navigate } from "react-router-dom";
import DemoWarningBanner from "./DemoWarningBanner";
import TopBar from "./TopBar";
import NavSidebar from "./NavSidebar";
import { useAuth } from "../hooks/useAuth";
import { usePresentationMode } from "../hooks/usePresentationMode";

export default function Layout() {
  const { user, loading } = useAuth();
  const { presentationMode } = usePresentationMode();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading SecureMed AI…</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className={`min-h-screen flex flex-col ${presentationMode ? "presentation-mode" : ""}`}>
      <DemoWarningBanner />
      <TopBar />
      <div className="flex flex-1 min-h-0">
        {!presentationMode && <NavSidebar />}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
