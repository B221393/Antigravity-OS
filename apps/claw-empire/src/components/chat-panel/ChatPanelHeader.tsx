import { useState } from "react";
import AgentAvatar from "../AgentAvatar";
import type { Agent, WorkflowPackKey } from "../../types";

type Tr = (ko: string, en: string, ja?: string, zh?: string) => string;

interface ChatPanelHeaderProps {
  selectedAgent: Agent | null;
  selectedDeptName?: string | null;
  spriteMap: ReturnType<typeof import("../AgentAvatar").buildSpriteMap>;
  tr: Tr;
  getAgentName: (agent: Agent | null | undefined) => string;
  getRoleLabel: (role: string) => string;
  getStatusLabel: (status: string) => string;
  statusColors: Record<string, string>;
  showAnnouncementBanner: boolean;
  visibleMessagesLength: number;
  onClearMessages?: (agentId?: string) => void;
  onClose: () => void;
  activeWorkflowPack?: WorkflowPackKey;
  onChangeWorkflowPack?: (packKey: WorkflowPackKey) => void;
}

export default function ChatPanelHeader({
  selectedAgent,
  selectedDeptName,
  spriteMap,
  tr,
  getAgentName,
  getRoleLabel,
  getStatusLabel,
  statusColors,
  showAnnouncementBanner,
  visibleMessagesLength,
  onClearMessages,
  onClose,
  activeWorkflowPack,
  onChangeWorkflowPack,
}: ChatPanelHeaderProps) {
  const [showPackMenu, setShowPackMenu] = useState(false);

  const packMeta: Record<string, { emoji: string; label: string }> = {
    development: { emoji: "🛠️", label: "Development" },
    novel: { emoji: "📚", label: "Novel Writing" },
    report: { emoji: "📊", label: "Structured Report" },
    video_preprod: { emoji: "🎬", label: "Video Pre-production" },
    web_research_report: { emoji: "🌐", label: "Web Research" },
    roleplay: { emoji: "🎭", label: "Roleplay" },
  };

  const packKeys = Object.keys(packMeta) as WorkflowPackKey[];

  return (
    <>
      <div className="chat-header flex flex-shrink-0 items-center gap-3 bg-gray-800 px-4 py-3">
        {selectedAgent ? (
          <>
            <div className="relative flex-shrink-0">
              <AgentAvatar agent={selectedAgent} spriteMap={spriteMap} size={40} />
              <span
                className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-gray-800 ${
                  statusColors[selectedAgent.status] ?? "bg-gray-500"
                }`}
              />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="truncate text-sm font-semibold text-white">{getAgentName(selectedAgent)}</span>
                <span className="rounded bg-gray-700 px-1.5 py-0.5 text-xs text-gray-300">
                  {getRoleLabel(selectedAgent.role)}
                </span>

                {activeWorkflowPack && (
                  <div className="relative">
                    <button
                      onClick={() => setShowPackMenu(!showPackMenu)}
                      className={`flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold transition-all border ${
                        activeWorkflowPack === "development"
                          ? "bg-gray-700 text-gray-400 border-gray-600 hover:bg-gray-600"
                          : "bg-blue-500/20 text-blue-400 border-blue-500/30 hover:bg-blue-500/30"
                      }`}
                    >
                      {packMeta[activeWorkflowPack]?.emoji || "📦"} {activeWorkflowPack.toUpperCase().replace(/_/g, " ")}
                      <span className="text-[8px] opacity-50">▼</span>
                    </button>

                    {showPackMenu && (
                      <>
                        <div className="fixed inset-0 z-[100]" onClick={() => setShowPackMenu(false)} />
                        <div className="absolute left-0 mt-1 z-[101] w-48 rounded-lg bg-gray-800 border border-gray-700 shadow-xl py-1">
                          {packKeys.map((key) => (
                            <button
                              key={key}
                              onClick={() => {
                                onChangeWorkflowPack?.(key);
                                setShowPackMenu(false);
                              }}
                              className={`w-full flex items-center gap-2 px-3 py-2 text-xs text-left transition-colors ${
                                activeWorkflowPack === key
                                  ? "bg-blue-600/20 text-blue-400 font-semibold"
                                  : "text-gray-300 hover:bg-gray-700 hover:text-white"
                              }`}
                            >
                              <span>{packMeta[key].emoji}</span>
                              <span>{packMeta[key].label}</span>
                              {activeWorkflowPack === key && <span className="ml-auto">✓</span>}
                            </button>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
              <div className="mt-0.5 flex items-center gap-1.5">
                <span className="truncate text-xs text-gray-400">{selectedDeptName}</span>
                <span className="text-gray-600">·</span>
                <span className="text-xs text-gray-400">{getStatusLabel(selectedAgent.status)}</span>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-yellow-500/20 text-xl">
              📢
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <div className="text-sm font-semibold text-white">
                  {tr("전사 공지", "Company Announcement", "全体告知", "全员公告")}
                </div>

                {activeWorkflowPack && (
                  <div className="relative">
                    <button
                      onClick={() => setShowPackMenu(!showPackMenu)}
                      className={`flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold transition-all border ${
                        activeWorkflowPack === "development"
                          ? "bg-gray-700 text-gray-400 border-gray-600 hover:bg-gray-600"
                          : "bg-blue-500/20 text-blue-400 border-blue-500/30 hover:bg-blue-500/30"
                      }`}
                    >
                      {packMeta[activeWorkflowPack]?.emoji || "📦"} {activeWorkflowPack.toUpperCase().replace(/_/g, " ")}
                      <span className="text-[8px] opacity-50">▼</span>
                    </button>

                    {showPackMenu && (
                      <>
                        <div className="fixed inset-0 z-[100]" onClick={() => setShowPackMenu(false)} />
                        <div className="absolute left-0 mt-1 z-[101] w-48 rounded-lg bg-gray-800 border border-gray-700 shadow-xl py-1">
                          {packKeys.map((key) => (
                            <button
                              key={key}
                              onClick={() => {
                                onChangeWorkflowPack?.(key);
                                setShowPackMenu(false);
                              }}
                              className={`w-full flex items-center gap-2 px-3 py-2 text-xs text-left transition-colors ${
                                activeWorkflowPack === key
                                  ? "bg-blue-600/20 text-blue-400 font-semibold"
                                  : "text-gray-300 hover:bg-gray-700 hover:text-white"
                              }`}
                            >
                              <span>{packMeta[key].emoji}</span>
                              <span>{packMeta[key].label}</span>
                              {activeWorkflowPack === key && <span className="ml-auto">✓</span>}
                            </button>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
              <div className="mt-0.5 text-xs text-gray-400">
                {tr(
                  "모든 에이전트에게 전달됩니다",
                  "Sent to all agents",
                  "すべてのエージェントに送信されます",
                  "将发送给所有代理",
                )}
              </div>
            </div>
          </>
        )}

        <div className="flex flex-shrink-0 items-center gap-1">
          {onClearMessages && visibleMessagesLength > 0 && (
            <button
              onClick={() => {
                if (
                  window.confirm(
                    selectedAgent
                      ? tr(
                          `${getAgentName(selectedAgent)}와의 대화를 삭제하시겠습니까?`,
                          `Delete conversation with ${getAgentName(selectedAgent)}?`,
                          `${getAgentName(selectedAgent)}との会話を削除しますか？`,
                          `要删除与 ${getAgentName(selectedAgent)} 的对话吗？`,
                        )
                      : tr(
                          "전사 공지 내역을 삭제하시겠습니까?",
                          "Delete announcement history?",
                          "全体告知履歴を削除しますか？",
                          "要删除全员公告记录吗？",
                        ),
                  )
                ) {
                  onClearMessages(selectedAgent?.id);
                }
              }}
              className="flex h-8 w-8 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-gray-700 hover:text-red-400"
              aria-label={tr("대화 내역 삭제", "Clear message history", "会話履歴を削除", "清除消息记录")}
              title={tr("대화 내역 삭제", "Clear message history", "会話履歴を削除", "清除消息记录")}
            >
              <svg
                className="block h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 6h18" />
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
              </svg>
            </button>
          )}

          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition-colors hover:bg-gray-700 hover:text-white"
            aria-label={tr("닫기", "Close", "閉じる", "关闭")}
          >
            ✕
          </button>
        </div>
      </div>

      {showAnnouncementBanner && (
        <div className="flex flex-shrink-0 items-center gap-2 border-b border-yellow-500/30 bg-yellow-500/10 px-4 py-2">
          <span className="text-sm font-medium text-yellow-400">
            📢{" "}
            {tr(
              "전사 공지 모드 - 모든 에이전트에게 전달됩니다",
              "Announcement mode - sent to all agents",
              "全体告知モード - すべてのエージェントに送信",
              "全员公告模式 - 将发送给所有代理",
            )}
          </span>
        </div>
      )}
    </>
  );
}
