"use client";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import { ChatWindow } from "@/components/chat-window";

export default function ChatPage() {
  return (
    <AuthGuard>
      <AppShell>
        <ChatWindow />
      </AppShell>
    </AuthGuard>
  );
}

