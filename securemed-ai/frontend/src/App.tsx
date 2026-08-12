import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import AIAssistant from "./pages/AIAssistant";
import Architecture from "./pages/Architecture";
import AuditLogs from "./pages/AuditLogs";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/assistant" element={<AIAssistant />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/audit" element={<AuditLogs />} />
      </Route>
      <Route path="*" element={<Navigate to="/assistant" replace />} />
    </Routes>
  );
}
