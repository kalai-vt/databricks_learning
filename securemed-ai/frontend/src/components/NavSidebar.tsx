import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, MessageSquareText, Building2, ShieldCheck, Radar,
  ScrollText, Cpu, Network, PlayCircle, Globe2,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/overview", label: "Overview", icon: LayoutDashboard },
  { to: "/assistant", label: "AI Assistant", icon: MessageSquareText },
  { to: "/tenants", label: "Tenants", icon: Building2 },
  { to: "/governance", label: "Governance", icon: ShieldCheck },
  { to: "/security", label: "Security Center", icon: Radar },
  { to: "/audit", label: "Audit Logs", icon: ScrollText },
  { to: "/model", label: "Model", icon: Cpu },
  { to: "/architecture", label: "Architecture", icon: Network },
  { to: "/guided-demo", label: "Guided Demo", icon: PlayCircle },
  { to: "/saas-use-cases", label: "SaaS Use Cases", icon: Globe2 },
];

export default function NavSidebar() {
  return (
    <nav className="w-56 shrink-0 bg-white border-r border-slate-200 py-4 hidden md:flex md:flex-col gap-1 overflow-y-auto">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm font-medium transition-colors ${
              isActive ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          <Icon size={17} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
