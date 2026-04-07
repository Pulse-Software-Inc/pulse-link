import { Avatar } from "@mui/material"
import { useRouter } from 'next/navigation';
import Image from "next/image"

export default function SettingsSidebar(props) {
  const router = useRouter()
  const name = props.name
  const allLinks = props.sidebarLabels
  const nav = props.navigation

  return (
    <aside
      className="hidden md:flex h-full w-[260px] shrink-0 flex-col justify-between px-6 py-8"
      style={{
        background:
          "linear-gradient(135deg, #5EEDFD 0%, #DDB1FC 50%, #FFBBC9 100%)",
      }}
    >
      <div>
        <div className="mb-8 items-center gap-3">
          <span className="text-m font-semibold text-white">{name}</span>
        </div>

        <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/50">
          Settings
        </p>
        <nav className="mb-6 flex flex-col gap-0.5">
          {allLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => nav.handleNavigate(link.id)}
              className={`rounded-md px-3 py-2 text-left text-[13px] font-medium transition-colors ${nav.activeSection === link.id
                ? "bg-white/25 text-white"
                : "text-white/75 hover:bg-white/10 hover:text-white"
                }`}
            >
              {link.label}
            </button>
          ))}
        </nav>
      </div>

      <button onClick={() => router.push('/auth/signout')} className="flex items-center gap-2 rounded-md px-3 py-2 text-left text-xl font-medium text-white/75 transition-colors hover:bg-white/10 hover:text-white">
        <Image src="/Sidebar/LogOut_Icon.svg" alt="Log Out" width={20} height={20} />
        Sign Out
      </button>
    </aside>
  );
}