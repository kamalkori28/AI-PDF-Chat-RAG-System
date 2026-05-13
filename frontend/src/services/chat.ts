import { API_URL } from "@/lib/constants";
import { api } from "@/services/api";
import { getToken } from "@/services/token";
import type {
  ChatRequest,
  ChatSession,
  HistoryResponse,
  StreamError,
  StreamMetadata
} from "@/types";

type StreamCallbacks = {
  onMetadata?: (metadata: StreamMetadata) => void;
  onToken?: (token: string) => void;
  onDone?: () => void | Promise<void>;
  onError?: (error: StreamError) => void;
};

export async function getHistory(): Promise<HistoryResponse> {
  const response = await api.get<HistoryResponse>("/history");
  return response.data;
}

export async function getSession(sessionId: string): Promise<ChatSession> {
  const response = await api.get<ChatSession>(`/history/${sessionId}`);
  return response.data;
}

export async function streamChat(payload: ChatRequest, callbacks: StreamCallbacks) {
  const token = getToken();
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let detail = "Streaming request failed";
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      // Keep the fallback when the response body is not JSON.
    }
    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error("Streaming response body is empty");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const eventBlock of events) {
      const event = parseSseEvent(eventBlock);
      if (!event) {
        continue;
      }
      if (event.type === "metadata") {
        callbacks.onMetadata?.(event.data as StreamMetadata);
      }
      if (event.type === "token") {
        callbacks.onToken?.((event.data as { token: string }).token);
      }
      if (event.type === "done") {
        await callbacks.onDone?.();
      }
      if (event.type === "error") {
        const error = event.data as StreamError;
        callbacks.onError?.(error);
        return;
      }
    }
  }
}

function parseSseEvent(block: string): { type: string; data: unknown } | null {
  const typeLine = block.split("\n").find((line) => line.startsWith("event:"));
  const dataLine = block.split("\n").find((line) => line.startsWith("data:"));
  if (!typeLine || !dataLine) {
    return null;
  }
  return {
    type: typeLine.replace("event:", "").trim(),
    data: JSON.parse(dataLine.replace("data:", "").trim())
  };
}
