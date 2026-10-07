import {
  useEffect,
  useState,
} from "react";

import {
  ArrowLeft,
  Bot,
  FileText,
  Send,
  Sparkles,
  User,
} from "lucide-react";

import { useSearchParams } from "react-router-dom";

import {
  sendChatMessage,
  type ChatResponse,
  type ChatSource,
} from "../api/chat";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  latency_ms?: number;
}

function Chat() {
  const [searchParams] = useSearchParams();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [conversationId, setConversationId] =
    useState<string | null>(null);

  const [llmMode, setLlmMode] = useState<
    "online" | "offline"
  >("offline");

  const [retrievalLimit, setRetrievalLimit] =
    useState(5);

  useEffect(() => {
    const question = searchParams.get("question");

    if (question) {
      setInput(question);
    }
  }, [searchParams]);

  async function handleSend() {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setError("");
    setInput("");

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: message,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);

    try {
      const response: ChatResponse =
        await sendChatMessage({
          message,
          conversation_id: conversationId,
          llm_mode: llmMode,
          retrieval_limit: retrievalLimit,
        });

      setConversationId(
        response.conversation_id
      );

      const assistantMessage: Message = {
        id: response.assistant_message_id,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        latency_ms: response.latency_ms,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (err) {
      console.error(
        "Chat request failed:",
        err
      );

      setError(
        "Unable to get a response from KnowledgeOps AI."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleSend();
    }
  }

  function renderSources(
    sources: ChatSource[]
  ) {
    if (!sources.length) {
      return null;
    }

    return (
      <div className="mt-4 border-t border-slate-200 pt-4">
        <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <FileText size={14} />
          Sources
        </div>

        <div className="space-y-2">
          {sources.map((source) => (
            <div
              key={source.chunk_id}
              className="rounded-lg border border-slate-200 bg-slate-50 p-3"
            >
              <p className="line-clamp-3 text-xs leading-5 text-slate-600">
                {source.text}
              </p>

              {source.distance !== null && (
                <p className="mt-2 text-[11px] text-slate-400">
                  Retrieval distance:{" "}
                  {source.distance.toFixed(4)}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() =>
                window.history.back()
              }
              className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
              title="Go back"
            >
              <ArrowLeft size={20} />
            </button>

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
              <Sparkles size={20} />
            </div>

            <div>
              <h1 className="font-bold text-slate-900">
                KnowledgeOps AI
              </h1>

              <p className="text-xs text-slate-500">
                Knowledge Assistant
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <select
              value={llmMode}
              onChange={(event) =>
                setLlmMode(
                  event.target.value as
                    | "online"
                    | "offline"
                )
              }
              disabled={loading}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 outline-none focus:border-indigo-500"
            >
              <option value="offline">
                Offline
              </option>

              <option value="online">
                Online
              </option>
            </select>

            <select
              value={retrievalLimit}
              onChange={(event) =>
                setRetrievalLimit(
                  Number(event.target.value)
                )
              }
              disabled={loading}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 outline-none focus:border-indigo-500"
            >
              <option value={3}>
                3 sources
              </option>

              <option value={5}>
                5 sources
              </option>

              <option value={10}>
                10 sources
              </option>
            </select>
          </div>
        </div>
      </header>

      {/* Chat area */}
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6">
        <div className="flex-1 py-8">
          {messages.length === 0 ? (
            <div className="flex min-h-[55vh] flex-col items-center justify-center text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200">
                <Bot size={30} />
              </div>

              <h2 className="mt-6 text-2xl font-bold text-slate-900">
                How can I help you?
              </h2>

              <p className="mt-2 max-w-lg text-sm leading-6 text-slate-500">
                Ask questions about your company's
                policies, procedures, documents,
                and internal knowledge.
              </p>

              <div className="mt-6 grid max-w-2xl gap-3 sm:grid-cols-2">
                <button
                  onClick={() =>
                    setInput(
                      "What is the employee leave policy?"
                    )
                  }
                  className="rounded-xl border border-slate-200 bg-white p-4 text-left text-sm text-slate-600 shadow-sm transition hover:border-indigo-300 hover:shadow-md"
                >
                  What is the employee leave policy?
                </button>

                <button
                  onClick={() =>
                    setInput(
                      "What are the company working hours?"
                    )
                  }
                  className="rounded-xl border border-slate-200 bg-white p-4 text-left text-sm text-slate-600 shadow-sm transition hover:border-indigo-300 hover:shadow-md"
                >
                  What are the company working hours?
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  {message.role ===
                    "assistant" && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
                      <Bot size={18} />
                    </div>
                  )}

                  <div
                    className={`max-w-3xl rounded-2xl px-5 py-4 ${
                      message.role === "user"
                        ? "bg-indigo-600 text-white"
                        : "border border-slate-200 bg-white text-slate-800 shadow-sm"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {message.role ===
                        "user" && (
                        <User size={15} />
                      )}

                      <span className="text-xs font-semibold">
                        {message.role ===
                        "user"
                          ? "You"
                          : "KnowledgeOps AI"}
                      </span>
                    </div>

                    <p className="mt-2 whitespace-pre-wrap text-sm leading-7">
                      {message.content}
                    </p>

                    {message.role ===
                      "assistant" &&
                      message.sources &&
                      renderSources(
                        message.sources
                      )}

                    {message.role ===
                      "assistant" &&
                      message.latency_ms !==
                        undefined && (
                        <p className="mt-3 text-[11px] text-slate-400">
                          Response time:{" "}
                          {message.latency_ms} ms
                        </p>
                      )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-4">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
                    <Bot size={18} />
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:150ms]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:300ms]" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Input */}
        <div className="sticky bottom-0 bg-slate-100 pb-6 pt-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-2 shadow-lg">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
                placeholder="Ask your company knowledge assistant..."
                className="max-h-40 min-h-[48px] flex-1 resize-none bg-transparent px-4 py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:opacity-50"
              />

              <button
                onClick={handleSend}
                disabled={
                  loading ||
                  !input.trim()
                }
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md transition hover:from-indigo-500 hover:to-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
                title="Send message"
              >
                <Send size={18} />
              </button>
            </div>
          </div>

          <p className="mt-2 text-center text-[11px] text-slate-400">
            KnowledgeOps AI can answer questions using
            your organization's knowledge base.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Chat;