import apiClient from "./client";

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
  llm_mode?: "online" | "offline" | null;
  retrieval_limit?: number;
}

export interface ChatSource {
  chunk_id: string;
  document_id: string;
  document_version_id: string;
  chunk_index: number;
  text: string;
  distance: number | null;
}

export interface ChatResponse {
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  answer: string;
  sources: ChatSource[];
  llm_mode: "online" | "offline";
  latency_ms: number;
}

export async function sendChatMessage(
  data: ChatRequest,
): Promise<ChatResponse> {
  const response =
    await apiClient.post<ChatResponse>(
      "/chat",
      data,
    );

  return response.data;
}