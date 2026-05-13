"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { FileText, LayoutDashboard, LogOut, MessageSquareText, UploadCloud } from "lucide-react";
import { ReactNode } from "react";
import clsx from "clsx";

import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/hooks/use-auth";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: UploadCloud },
  { href: "/chat", label: "Chat", icon: MessageSquareText }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-[var(--border)] bg-[var(--surface)] p-4 lg:block">
        <Link className="mb-8 flex items-center gap-3" href="/dashboard">
          <div className="icon-btn" aria-hidden>
            <FileText size={20} />
          </div>
          <div>
            <p className="font-bold leading-tight">Enterprise AI</p>
            <p className="muted text-xs">PDF Chat</p>
          </div>
        </Link>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                className={clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-bold",
                  pathname === item.href
                    ? "bg-[var(--surface-strong)] text-[var(--primary)]"
                    : "text-[var(--muted)] hover:bg-[var(--surface-strong)] hover:text-[var(--text)]"
                )}
                href={item.href}
                key={item.href}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--surface)]/90 px-4 py-3 backdrop-blur">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
            <nav className="flex gap-1 lg:hidden">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link className="icon-btn" href={item.href} key={item.href} title={item.label}>
                    <Icon size={18} />
                  </Link>
                );
              })}
            </nav>
            <div className="ml-auto flex items-center gap-2">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-bold">{user?.full_name ?? "User"}</p>
                <p className="muted text-xs">{user?.email}</p>
              </div>
              <ThemeToggle />
              <button className="icon-btn" onClick={handleLogout} title="Sign out" type="button">
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}

