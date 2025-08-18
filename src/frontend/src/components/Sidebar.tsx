
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import DashboardIcon from "../SidebarIcons/DashboardIcon";
import ResearchIcon from "../SidebarIcons/ResearchIcon";
import ReportIcon from "../SidebarIcons/ReportIcon";
import SavedIcon from "../SidebarIcons/SavedIcon";
import SupportIcon from "../SidebarIcons/SupportIcon";
import SettingIcon from "../SidebarIcons/SettingIcon";

function Sidebar() {
  const [isHovered, setIsHovered] = useState(false);
  const location = useLocation();

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: DashboardIcon },
    { name: "Research", path: "/research", icon: ResearchIcon },
    { name: "Report", path: "/report", icon: ReportIcon },
    { name: "Saved", path: "/saved", icon: SavedIcon },
    { name: "Support", path: "/support", icon: SupportIcon },
    { name: "Setting", path: "/setting", icon: SettingIcon },
  ];

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`h-[545px] bg-white shadow-md transition-all duration-300 ease-in-out ${
        isHovered ? "w-[230px]" : "w-[64px]"
      }`}
    >
      <ul className="space-y-2 p-2">
        {menuItems.map(({ name, path, icon: Icon }) => {
          const isActive = location.pathname === path;

          return (
            <li key={name}>
              <Link
                to={path}
                className={`flex items-center gap-3 p-2 rounded-lg transition-all ${
                  isActive
                    ? "bg-[#E5F1FF] font-semibold text-black-600"
                    : "hover:bg-[#E5F1FF]"
                }`}
              >
                <Icon />
                <span
                  className={`transition-opacity duration-300 text-sm ${
                    isHovered ? "opacity-100 ml-1" : "opacity-0 w-0 overflow-hidden"
                  }`}
                >
                  {name}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Sidebar;
