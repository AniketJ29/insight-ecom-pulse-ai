
import { ReactNode, useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";
import { Header } from "./Header";
import { SidebarNav } from "./SidebarNav";
import { Sidebar, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const isMobile = useIsMobile();

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulate refresh
    setTimeout(() => {
      setIsRefreshing(false);
      window.location.reload();
    }, 1000);
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <Sidebar defaultCollapsed={isMobile}>
          <SidebarNav />
        </Sidebar>
        <div className="flex flex-col flex-1">
          <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />
          <main className="flex-1">
            <div className="container py-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                <SidebarTrigger />
              </div>
              {children}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
