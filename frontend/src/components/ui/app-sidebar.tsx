import { useEffect, useState } from "react";
import { auth } from "@/firebase/firebaseConfig";
import {
  CalendarCheck,
  HelpCircle,
  MessageCircle,
  Newspaper,
  Sun,
  Tag,
  Settings,
} from "lucide-react";

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
import { Tooltip } from "@radix-ui/react-tooltip";

// Menu items.
const items = [
  {
    title: "FAQ Générale",
    url: "#",
    icon: HelpCircle, // Icône pour l'aide ou FAQ
  },
  {
    title: "Support Technique",
    url: "#",
    icon: Tooltip, // Icône pour le support technique
  },
  {
    title: "Météo",
    url: "#",
    icon: Sun, // Icône pour la météo
  },
  {
    title: "Actualités",
    url: "#",
    icon: Newspaper, // Icône pour les actualités
  },
  {
    title: "Réservations",
    url: "#",
    icon: CalendarCheck, // Icône pour les réservations
  },
  {
    title: "Promotions",
    url: "#",
    icon: Tag, // Icône pour les promotions
  },
  {
    title: "Compte",
    url: "#",
    icon: Settings, // Icône pour le compte utilisateur
  },
  {
    title: "Suggestions",
    url: "#",
    icon: MessageCircle, // Icône pour les suggestions
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
            <SidebarGroupLabel>
              <p className="text-lg">{username ? username : "Loading..."}</p>
              <a href="/settings">
                <Settings height={16} width={16} className="ml-20" />{" "}
                {/* Icône d'engrenage */}
              </a>
            </SidebarGroupLabel>
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
            Déconnexion
          </Button>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
