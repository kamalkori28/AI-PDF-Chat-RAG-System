"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Bot, FileText, History, Plus, Send, Sparkles, User } from "lucide-react";
import { toast } from "sonner";

import { SourceList } from "@/components/source-list";
import { useDocuments } from "@/hooks/use-documents";
import { useHistory } from "@/hooks/use-history";
import { getSession, streamChat } from "@/services/chat";
import { getErrorMessage } from "@/services/errors";
import type { Citation, MessageRecord } from "@/types";

type LocalMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

export function ChatWindow() {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [loadingSessionId, setLoadingSessionId] = useState<string | null>(null);
  const assistantIdRef = useRef<string | null>(null);
  const { data: documents } = useDocuments();
  const { data: history, refetch: refetchHistory } = useHistory();

  const readyDocuments = useMemo(
    () => (documents ?? []).filter((document) => document.status === "ready"),
    [documents]
  );

  function newChat() {
    setMessages([]);
    setSessionId(null);
    setSelectedDocumentIds([]);
  }

  function toggleDocument(documentId: string) {
    setSelectedDocumentIds((current) =>
      current.includes(documentId)
        ? current.filter((id) => id !== documentId)
        : [...current, documentId]
    );
  }

  async function openSession(targetSessionId: string) {
    setLoadingSessionId(targetSessionId);
    try {
      const session = await getSession(targetSessionId);
      setSessionId(session.id);
      setMessages(session.messages.map(toLocalMessage));
      setSelectedDocumentIds([]);
    } catch (error) {
      toast.error(getErrorMessage(error, "Could not load chat history"));
    } finally {
      setLoadingSessionId(null);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || streaming) {
      return;
    }

    const userMessage: LocalMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed
    };
    const assistantMessage: LocalMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: ""
    };
    assistantIdRef.current = assistantMessage.id;

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setInput("");
    setStreaming(true);

    try {
      await streamChat(
        {
          message: trimmed,
          session_id: sessionId,
          document_ids: selectedDocumentIds.length ? selectedDocumentIds : null,
          top_k: 5,
          hybrid: true
        },
        {
          onMetadata: (metadata) => {
            setSessionId(metadata.session_id);
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantMessage.id
                  ? { ...message, citations: metadata.citations }
                  : message
              )
            );
          },
          onToken: (token) => {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantIdRef.current
                  ? { ...message, content: message.content + token }
                  : message
              )
            );
          },
          onDone: async () => {
            await refetchHistory();
          },
          onError: (error) => {
            toast.error(error.detail);
          }
        }
      );
    } catch (error) {
      toast.error(getErrorMessage(error, "Chat request failed"));
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessage.id
            ? { ...message, content: "I could not complete this request." }
            : message
        )
      );
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="grid min-h-[calc(100vh-7rem)] gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section className="panel flex min-h-[calc(100vh-7rem)] flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-[var(--border)] p-4">
          <div className="flex items-center gap-3">
            <div className="icon-btn" aria-hidden>
              <Sparkles size={18} />
            </div>
            <div>
              <h1 className="font-bold">Chat</h1>
              <p className="muted text-xs">{sessionId ? "Active session" : "New session"}</p>
            </div>
          </div>
          <button className="icon-btn" onClick={newChat} title="New chat" type="button">
            <Plus size={18} />
          </button>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {!messages.length ? (
            <div className="grid h-full min-h-[340px] place-items-center">
              <div className="text-center">
                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface-strong)]">
                  <FileText size={22} />
                </div>
                <p className="font-bold">Ask a question</p>
                <p className="muted text-sm">PDF context ready</p>
              </div>
            </div>
          ) : null}

          {messages.map((message) => (
            <article
              className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              key={message.id}
            >
              {message.role === "assistant" ? (
                <div className="icon-btn mt-1 shrink-0" aria-hidden>
                  <Bot size={17} />
                </div>
              ) : null}
              <div
                className={`max-w-[82%] rounded-lg border border-[var(--border)] p-3 ${
                  message.role === "user"
                    ? "bg-[var(--primary)] text-white"
                    : "bg-[var(--surface)] text-[var(--text)]"
                }`}
              >
                {message.content ? (
                  <div className="markdown">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--primary)]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--accent)] [animation-delay:120ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--warning)] [animation-delay:240ms]" />
                  </div>
                )}
                {message.citations?.length ? <SourceList citations={message.citations} compact /> : null}
              </div>
              {message.role === "user" ? (
                <div className="icon-btn mt-1 shrink-0" aria-hidden>
                  <User size={17} />
                </div>
              ) : null}
            </article>
          ))}
        </div>

        <form className="border-t border-[var(--border)] p-4" onSubmit={onSubmit}>
          <div className="flex gap-2">
            <textarea
              className="input min-h-12 resize-none"
              rows={1}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about your PDFs"
            />
            <button className="btn btn-primary shrink-0" disabled={streaming} type="submit">
              <Send size={18} />
              Send
            </button>
          </div>
        </form>
      </section>

      <aside className="panel h-fit p-4">
        <div className="grid gap-5">
          <section>
            <h2 className="mb-3 flex items-center gap-2 font-bold">
              <FileText size={17} />
              Sources
            </h2>
            <div className="space-y-2">
              {readyDocuments.map((document) => (
                <button
                  className={`soft-panel flex w-full items-center gap-3 p-3 text-left ${
                    selectedDocumentIds.includes(document.id)
                      ? "border-[var(--primary)]"
                      : "border-[var(--border)]"
                  }`}
                  key={document.id}
                  onClick={() => toggleDocument(document.id)}
                  type="button"
                >
                  <FileText className="shrink-0 text-[var(--accent)]" size={18} />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-bold">{document.filename}</p>
                    <p className="muted text-xs">{document.chunk_count} chunks</p>
                  </div>
                </button>
              ))}
              {!readyDocuments.length ? <p className="muted text-sm">No ready documents</p> : null}
            </div>
          </section>

          <section>
            <h2 className="mb-3 flex items-center gap-2 font-bold">
              <History size={17} />
              History
            </h2>
            <div className="space-y-2">
              {(history?.sessions ?? []).slice(0, 8).map((session) => (
                <button
                  className={`soft-panel w-full p-3 text-left ${
                    session.id === sessionId ? "border-[var(--primary)]" : "border-[var(--border)]"
                  }`}
                  disabled={loadingSessionId === session.id}
                  key={session.id}
                  onClick={() => openSession(session.id)}
                  type="button"
                >
                  <p className="truncate text-sm font-bold">{session.title}</p>
                  <p className="muted text-xs">
                    {loadingSessionId === session.id
                      ? "Loading"
                      : `${session.messages.length} messages`}
                  </p>
                </button>
              ))}
              {!history?.sessions.length ? <p className="muted text-sm">No previous chats</p> : null}
            </div>
          </section>
        </div>
      </aside>
    </div>
  );
}

function toLocalMessage(message: MessageRecord): LocalMessage {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    citations: message.citations ?? undefined
  };
}
