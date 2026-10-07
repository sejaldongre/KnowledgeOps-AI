import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  ArrowRight,
  FileText,
  MessageSquare,
  Search,
  Sparkles,
  Upload,
} from "lucide-react";

import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [question, setQuestion] = useState("");

  const firstName =
    user?.full_name?.split(" ")[0] || "there";

  function handleAskAI() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }

    navigate(
      `/chat?question=${encodeURIComponent(trimmedQuestion)}`
    );
  }

  function handleQuestionKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleAskAI();
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="min-w-0 flex-1">
        {/* Top bar */}
        <header className="flex h-20 items-center justify-between border-b border-slate-200 bg-white px-8">
          <div>
            <p className="text-sm text-slate-500">
              Knowledge workspace
            </p>

            <h2 className="text-lg font-semibold text-slate-900">
              AI Knowledge Assistant
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-2 rounded-full bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-700 sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              AI services online
            </div>

            <button
              onClick={logout}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Main content */}
        <div className="mx-auto max-w-7xl px-8 py-10">
          {/* Welcome */}
          <section>
            <div className="flex items-center gap-2 text-sm font-medium text-indigo-600">
              <Sparkles size={16} />
              Intelligent knowledge workspace
            </div>

            <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900">
              Good evening, {firstName} 👋
            </h1>

            <p className="mt-3 max-w-2xl text-base text-slate-500">
              Search your company knowledge, ask questions,
              and get answers grounded in your organization's
              documents.
            </p>
          </section>

          {/* AI Search */}
          <section className="mt-8">
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-blue-600 to-violet-600 p-8 shadow-xl shadow-indigo-200">
              <div className="absolute -right-20 -top-20 h-56 w-56 rounded-full bg-white/10 blur-3xl" />

              <div className="relative">
                <div className="flex items-center gap-2 text-sm font-medium text-indigo-100">
                  <Sparkles size={17} />
                  Ask KnowledgeOps AI
                </div>

                <h2 className="mt-3 text-2xl font-bold text-white">
                  What would you like to know?
                </h2>

                <p className="mt-2 text-sm text-indigo-100">
                  Ask questions about policies, procedures,
                  benefits, projects, and internal documentation.
                </p>

                <div className="mt-6 flex flex-col gap-3 rounded-xl bg-white p-2 shadow-lg sm:flex-row">
                  <div className="flex flex-1 items-center gap-3 px-3">
                    <Search
                      size={20}
                      className="text-slate-400"
                    />

                    <input
                      type="text"
                      value={question}
                      onChange={(event) =>
                        setQuestion(event.target.value)
                      }
                      onKeyDown={handleQuestionKeyDown}
                      placeholder="Ask about your company knowledge..."
                      className="w-full bg-transparent py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400"
                    />
                  </div>

                  <button
                    onClick={handleAskAI}
                    disabled={!question.trim()}
                    className="flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Ask AI
                    <ArrowRight size={17} />
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Quick actions */}
          <section className="mt-10">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  Quick actions
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Manage and explore your knowledge workspace.
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-5 md:grid-cols-3">
              {/* Chat */}
              <button
                onClick={() => navigate("/chat")}
                className="group rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-lg"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 transition group-hover:bg-indigo-600 group-hover:text-white">
                  <MessageSquare size={22} />
                </div>

                <h3 className="mt-5 text-lg font-semibold text-slate-900">
                  Start a conversation
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Ask the AI assistant questions using your
                  company's knowledge base.
                </p>

                <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-indigo-600">
                  Start chat
                  <ArrowRight size={16} />
                </div>
              </button>

              {/* Documents */}
              <button
                onClick={() => navigate("/documents")}
                className="group rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:border-blue-200 hover:shadow-lg"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white">
                  <FileText size={22} />
                </div>

                <h3 className="mt-5 text-lg font-semibold text-slate-900">
                  Manage documents
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Upload and manage company policies,
                  guides, and internal documentation.
                </p>

                <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-blue-600">
                  View documents
                  <ArrowRight size={16} />
                </div>
              </button>

              {/* Upload */}
              <button
                onClick={() => navigate("/documents")}
                className="group rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:border-violet-200 hover:shadow-lg"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-50 text-violet-600 transition group-hover:bg-violet-600 group-hover:text-white">
                  <Upload size={22} />
                </div>

                <h3 className="mt-5 text-lg font-semibold text-slate-900">
                  Upload knowledge
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Add new company documents to make them
                  available to the AI assistant.
                </p>

                <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-violet-600">
                  Upload document
                  <ArrowRight size={16} />
                </div>
              </button>
            </div>
          </section>

          {/* Recent activity */}
          <section className="mt-10">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">
                    Recent activity
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Your latest knowledge workspace activity.
                  </p>
                </div>

                <button className="text-sm font-semibold text-indigo-600 hover:text-indigo-700">
                  View all
                </button>
              </div>

              <div className="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-sm">
                  <MessageSquare
                    size={20}
                    className="text-slate-400"
                  />
                </div>

                <h3 className="mt-4 font-semibold text-slate-700">
                  No recent activity
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Start a conversation or upload a document
                  to get started.
                </p>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer className="py-8 text-center text-xs text-slate-400">
            KnowledgeOps AI · Enterprise Knowledge Platform
          </footer>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;