import { Sidebar } from "@/components/shell/sidebar";
import { TopBar } from "@/components/shell/top-bar";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div
        className={cn(
          "flex flex-col flex-1",
          "ml-[var(--sidebar-width)]"
        )}
      >
        <TopBar />
        <main
          className={cn(
            "flex-1 overflow-y-auto",
            "pt-[var(--topbar-height)] p-6"
          )}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
