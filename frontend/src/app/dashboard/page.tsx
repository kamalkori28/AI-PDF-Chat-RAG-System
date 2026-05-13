"use client";

import Link from "next/link";
import { FileText, MessageSquareText, UploadCloud } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import { StatCard } from "@/components/stat-card";
import { useDocuments } from "@/hooks/use-documents";
import { useHistory } from "@/hooks/use-history";

export default function DashboardPage() {
  const { data: documents, isLoading: docsLoading } = useDocuments();
  const { data: history, isLoading: historyLoading } = useHistory();
  const readyDocuments = documents?.filter((document) => document.status === "ready").length ?? 0;

  return (
    <AuthGuard>
      <AppShell>
        <div className="grid gap-5">
          <header className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h1 className="text-2xl font-bold">Dashboard</h1>
              <p className="muted text-sm">Enterprise AI PDF Chat</p>
            </div>
            <div className="flex gap-2">
              <Link className="btn btn-secondary" href="/upload">
                <UploadCloud size={18} />
                Upload
              </Link>
              <Link className="btn btn-primary" href="/chat">
                <MessageSquareText size={18} />
                Chat
              </Link>
            </div>
          </header>

          <section className="grid gap-4 md:grid-cols-3">
            <StatCard
              icon={FileText}
              label="Documents"
              loading={docsLoading}
              value={documents?.length ?? 0}
            />
            <StatCard
              icon={UploadCloud}
              label="Ready"
              loading={docsLoading}
              value={readyDocuments}
            />
            <StatCard
              icon={MessageSquareText}
              label="Sessions"
              loading={historyLoading}
              value={history?.sessions.length ?? 0}
            />
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="panel p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold">Recent Documents</h2>
                <Link className="text-sm font-bold text-[var(--primary)]" href="/upload">
                  Manage
                </Link>
              </div>
              <div className="space-y-3">
                {(documents ?? []).slice(0, 5).map((document) => (
                  <div className="soft-panel flex items-center justify-between gap-3 p-3" key={document.id}>
                    <div className="min-w-0">
                      <p className="truncate font-semibold">{document.filename}</p>
                      <p className="muted text-xs">
                        {document.status} - {document.chunk_count} chunks
                      </p>
                    </div>
                    <FileText className="shrink-0 text-[var(--accent)]" size={20} />
                  </div>
                ))}
                {!docsLoading && !documents?.length ? (
                  <div className="soft-panel p-4 text-sm muted">No documents</div>
                ) : null}
              </div>
            </div>

            <div className="panel p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold">Recent Chats</h2>
                <Link className="text-sm font-bold text-[var(--primary)]" href="/chat">
                  Open
                </Link>
              </div>
              <div className="space-y-3">
                {(history?.sessions ?? []).slice(0, 5).map((session) => (
                  <div className="soft-panel p-3" key={session.id}>
                    <p className="truncate font-semibold">{session.title}</p>
                    <p className="muted text-xs">{session.messages.length} messages</p>
                  </div>
                ))}
                {!historyLoading && !history?.sessions.length ? (
                  <div className="soft-panel p-4 text-sm muted">No chats</div>
                ) : null}
              </div>
            </div>
          </section>
        </div>
      </AppShell>
    </AuthGuard>
  );
}

