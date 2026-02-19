import React from "react";
import Image from "next/image";

// Sidebar navigation data for each of the menu items, including title, icon, and link
const doctorSidebarData = [
    {
        title: "Dashboard",
        icon: <Image src="/Dashboard_Icon.svg" alt="Dashboard" width={24} height={24} />,
        link: "/userdashboard"
    },
    {
        title: "Settings",
        icon: <Image src="/Settings_Icon.svg" alt="Settings" width={24} height={24} />,
        link: "/auth/settings"
    },
];

export default doctorSidebarData;

