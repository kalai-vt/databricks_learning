import { AlertTriangle } from "lucide-react";

export default function DemoWarningBanner() {
  return (
    <div className="bg-amber-500 text-amber-950 text-center text-xs sm:text-sm font-semibold py-1.5 px-3 flex items-center justify-center gap-2">
      <AlertTriangle size={14} className="shrink-0" />
      <span>DEMO ENVIRONMENT — SYNTHETIC HEALTHCARE DATA — NOT FOR MEDICAL USE</span>
    </div>
  );
}
