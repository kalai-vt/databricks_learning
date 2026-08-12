import { NavLink } from "react-router-dom";
import { MessageSquareText, Network, ScrollText } from "lucide-react";

const NAV_ITEMS = [
  { to: "/assistant", label: "AI Assistant", icon: MessageSquareText },
  { to: "/architecture", label: "Architecture", icon: Network },
  { to: "/audit", label: "Audit Log", icon: ScrollText },
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
