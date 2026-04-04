import React from "react";
import Image from "next/image";

// Sidebar navigation data for each of the menu items, including title, icon, and link
const SidebarData = [
    {
        title: "Dashboard",
        icon: <Image src="/Sidebar/Dashboard_Icon.svg" alt="Dashboard" width={24} height={24} />,
        link: "/userdashboard"
    },
    {
        title: "Settings",
        icon: <Image src="/Sidebar/Settings_Icon.svg" alt="Settings" width={24} height={24} />,
        link: "/auth/settings"
    },
    {  
        title: "Devices",
        icon: <Image src="/Sidebar/Devices_Icon.svg" alt="Devices" width={24} height={24} />,
        link: "/auth/devices"
    },
    {
        title: "Companion",
        icon: <Image src="/Sidebar/Companion_Icon.svg" alt="Companion" width={24} height={24} />,
        link: "/auth/companions"
    }
];

export default SidebarData;

