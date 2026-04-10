import React from "react";
import Image from "next/image";

// Sidebar navigation data for each of the menu items, including title, icon, and link
const SidebarData = [
    {
        title: "Dashboard",
        icon: <Image src="/Sidebar/Dashboard_Icon.svg" alt="Dashboard" width={24} height={24} />,
        link: "/main/user-dashboard"
    },
    {
        title: "Settings",
        icon: <Image src="/Sidebar/Settings_Icon.svg" alt="Settings" width={24} height={24} />,
        link: "/util/settings?role=user"
    },
];

export default SidebarData;

