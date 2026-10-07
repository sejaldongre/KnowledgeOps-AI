import {
  FileText,
  MessageSquare,
  Search,
  Settings,
  Plus,
  ShieldCheck,
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

interface SidebarProps {
  onNewChat?: () => void;
}

function Sidebar({ onNewChat }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const isChatActive =
    location.pathname === "/chat" ||
    location.pathname === "/";

  const isDocumentsActive =
    location.pathname === "/documents";

  return (
    <aside className="flex min-h-screen w-64 flex-col bg-slate-950 text-white">
      {/* Logo */}
      <div className="border-b border-slate-800 px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 shadow-lg shadow-blue-500/20">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h1 className="font-bold tracking-tight">
              KnowledgeOps
            </h1>

            <p className="text-xs text-slate-400">
              AI Knowledge Platform
            </p>
          </div>
        </div>
      </div>

      {/* New chat */}
      <div className="px-4 pt-6">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-4 py-3 text-sm font-semibold shadow-lg shadow-blue-900/20 transition hover:from-blue-500 hover:to-violet-500"
        >
          <Plus size={18} />
          New conversation
        </button>
      </div>

      {/* Navigation */}
      <nav className="mt-8 flex-1 px-4">
        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Workspace
        </p>

        <div className="space-y-1">
          {/* Chat */}
          <button
            onClick={() => navigate("/chat")}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
              isChatActive
                ? "bg-slate-800 text-white"
                : "text-slate-300 hover:bg-slate-900 hover:text-white"
            }`}
          >
            <MessageSquare size={18} />
            Chat
          </button>

          {/* Documents */}
          <button
            onClick={() => navigate("/documents")}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
              isDocumentsActive
                ? "bg-slate-800 text-white"
                : "text-slate-300 hover:bg-slate-900 hover:text-white"
            }`}
          >
            <FileText size={18} />
            Documents
          </button>

          {/* Search - not implemented yet */}
          <button
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
          >
            <Search size={18} />
            Search
          </button>
        </div>

        <p className="mb-3 mt-8 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          System
        </p>

        {/* Settings - not implemented yet */}
        <button
          className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
        >
          <Settings size={18} />
          Settings
        </button>
      </nav>

      {/* Bottom */}
      <div className="border-t border-slate-800 p-4">
        <div className="flex items-center gap-3 rounded-xl bg-slate-900 p-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-sm font-bold">
            U
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-medium">
              Workspace user
            </p>

            <p className="text-xs text-slate-500">
              KnowledgeOps
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;