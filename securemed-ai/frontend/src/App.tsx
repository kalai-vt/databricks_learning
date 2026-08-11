import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Overview from "./pages/Overview";
import AIAssistant from "./pages/AIAssistant";
import Tenants from "./pages/Tenants";
import Governance from "./pages/Governance";
import SecurityCenter from "./pages/SecurityCenter";
import AuditLogs from "./pages/AuditLogs";
import ModelPage from "./pages/ModelPage";
import Architecture from "./pages/Architecture";
import GuidedDemo from "./pages/GuidedDemo";
import SaaSUseCases from "./pages/SaaSUseCases";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/overview" element={<Overview />} />
        <Route path="/assistant" element={<AIAssistant />} />
        <Route path="/tenants" element={<Tenants />} />
        <Route path="/governance" element={<Governance />} />
        <Route path="/security" element={<SecurityCenter />} />
        <Route path="/audit" element={<AuditLogs />} />
        <Route path="/model" element={<ModelPage />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/guided-demo" element={<GuidedDemo />} />
        <Route path="/saas-use-cases" element={<SaaSUseCases />} />
      </Route>
      <Route path="*" element={<Navigate to="/overview" replace />} />
    </Routes>
  );
}
