"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

import { useAuth } from "@/hooks/use-auth";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { ready, token } = useAuth();

  useEffect(() => {
    if (ready && !token) {
      router.replace("/login");
    }
  }, [ready, router, token]);

  if (!ready || !token) {
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="h-12 w-12 rounded-lg skeleton" />
      </main>
    );
  }

  return children;
}

