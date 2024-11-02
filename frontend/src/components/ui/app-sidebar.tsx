import { useEffect, useState } from "react";
import { auth } from "@/firebase/firebaseConfig";
import { Calendar, Home, Inbox, Search, Settings } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Button } from "./button";

// Menu items.
const items = [
  {
    title: "Home",
    url: "#",
    icon: Home,
  },
  {
    title: "Inbox",
    url: "#",
    icon: Inbox,
  },
  {
    title: "Calendar",
    url: "#",
    icon: Calendar,
  },
  {
    title: "Search",
    url: "#",
    icon: Search,
  },
  {
    title: "Settings",
    url: "#",
    icon: Settings,
  },
];

export function AppSidebar({ onLogout }: { onLogout: () => void }) {
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const user = auth.currentUser; // Get the current user
    if (user) {
      setUsername(user.displayName || user.email); // Use displayName or email as username
    }
  }, []);

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <div className="flex justify-between w-full items-center mt-1.5">
          <SidebarGroupLabel>{username ? username : "Loading..."}</SidebarGroupLabel>
            <SidebarTrigger />
          </div>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
          <Button
            onClick={onLogout} // Appelle la fonction de déconnexion
            className="bg-red-600 text-white mb-2 mt-auto">
            Logout
          </Button>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
