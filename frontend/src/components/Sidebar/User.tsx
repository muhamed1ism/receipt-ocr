import { Link as RouterLink } from "@tanstack/react-router"
import { ChevronsUpDown, LogOut, Settings } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { getInitials } from "@/utils"

interface UserInfoProps {
  first_name?: string
  last_name?: string
  email?: string
}

function UserInfo({ first_name, last_name, email }: UserInfoProps) {
  return (
    <div className="flex items-center gap-2.5 w-full min-w-0">
      <Avatar className="size-8">
        <AvatarFallback className="bg-primary font-semibold text-white">
          {getInitials(`${first_name} ${last_name}` || "Korisnik")}
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col items-start min-w-0">
        <p className="text-sm font-semibold truncate w-full">
          {first_name} {last_name}
        </p>
        <p className="text-xs text-muted-foreground truncate w-full">{email}</p>
      </div>
    </div>
  )
}

export function User({ user, profile }: { user: any; profile: any }) {
  const { logout } = useAuth()
  const { isMobile, setOpenMobile } = useSidebar()
  const borderDashed =
    "border-2 border-foreground/0 data-[state=open]:bg-sidebar-accent data-[state=open]:border-2 data-[state=open]:border-dashed data-[state=open]:border-foreground/30 hover:border-dashed hover:border-2 hover:border-foreground/10 data-[state=open]:text-sidebar-accent-foreground"

  if (!user) return null

  const handleMenuClick = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }
  const handleLogout = async () => {
    logout()
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton size="lg" data-testid="user-menu">
              <UserInfo
                first_name={profile?.first_name}
                last_name={profile?.last_name}
                email={user?.email}
              />
              <ChevronsUpDown className="ml-auto size-4 text-muted-foreground" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="font-receipt w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg font-semibold"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <UserInfo
                first_name={profile?.first_name}
                last_name={profile?.last_name}
                email={user?.email}
              />
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-transparent border-t-1 border-foreground/30 border-dashed" />
            <RouterLink to="/settings" onClick={handleMenuClick}>
              <DropdownMenuItem className={borderDashed}>
                <Settings />
                Postavke korisnika
              </DropdownMenuItem>
            </RouterLink>
            <DropdownMenuItem className={borderDashed} onClick={handleLogout}>
              <LogOut />
              Odjavi se
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
