import { useEffect, useState } from "react";
import type { WorkflowPackConfig } from "../../api/workflow-skills-subtasks";
import { getWorkflowPacks, updateWorkflowPack } from "../../api/workflow-skills-subtasks";
import type { LocalSettings, SetLocalSettings, TFunction } from "./types";

interface WorkflowPacksTabProps {
  t: TFunction;
  form: LocalSettings;
  setForm: SetLocalSettings;
  persistSettings: (next: LocalSettings) => void;
}

export default function WorkflowPacksTab({ t, form, setForm, persistSettings }: WorkflowPacksTabProps) {
  const [packs, setPacks] = useState<WorkflowPackConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getWorkflowPacks()
      .then((data) => setPacks(data.packs))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleTogglePack = async (key: string, enabled: boolean) => {
    setUpdating(key);
    try {
      await updateWorkflowPack(key as any, { enabled });
      setPacks((prev) => prev.map((p) => (p.key === key ? { ...p, enabled } : p)));
    } catch (err) {
      console.error("Toggle pack failed:", err);
    } finally {
      setUpdating(null);
    }
  };

  const handleSetDefaultPack = (key: string) => {
    const next = { ...form, officeWorkflowPack: key as any };
    setForm(next);
    persistSettings(next);
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500">
        <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-current border-t-transparent" />
        <p className="mt-2 text-sm">
          {t({
            ko: "팩 목록 불러오는 중...",
            en: "Loading packs...",
            ja: "パック一覧を読み込み中...",
            zh: "正在加载包列表...",
          })}
        </p>
      </div>
    );
  }

  return (
    <section
      className="rounded-xl p-5 sm:p-6 space-y-6"
      style={{ background: "var(--th-card-bg)", border: "1px solid var(--th-card-border)" }}
    >
      <div className="space-y-1">
        <h3 className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--th-text-primary)" }}>
          {t({
            ko: "워크플로우 팩 관리",
            en: "Workflow Packs",
            ja: "ワークフローパック管理",
            zh: "工作流包管理",
          })}
        </h3>
        <p className="text-xs" style={{ color: "var(--th-text-secondary)" }}>
          {t({
            ko: "활성화된 팩은 태스크 생성 및 자동 라우팅에 사용됩니다.",
            en: "Enabled packs are used for task creation and auto-routing.",
            ja: "有効なパックはタスク作成や自動ルーティングに使用されます。",
            zh: "启用的包将用于任务创建和自动路由。",
          })}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {packs.map((pack) => {
          const isDefault = form.officeWorkflowPack === pack.key;
          const isUpdating = updating === pack.key;

          return (
            <div
              key={pack.key}
              className={`relative overflow-hidden rounded-xl border p-4 transition-all ${
                isDefault ? "ring-2 ring-blue-500/50 shadow-lg shadow-blue-500/10" : ""
              }`}
              style={{
                background: "var(--th-input-bg)",
                borderColor: isDefault ? "var(--th-accent)" : "var(--th-card-border)",
              }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm" style={{ color: "var(--th-text-primary)" }}>
                      {pack.name}
                    </span>
                    {isDefault && (
                      <span className="rounded-full bg-blue-500/20 px-2 py-0.5 text-[10px] font-bold text-blue-400 border border-blue-500/30">
                        DEFAULT
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] font-mono opacity-60" style={{ color: "var(--th-text-secondary)" }}>
                    {pack.key}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleTogglePack(pack.key, !pack.enabled)}
                    disabled={isUpdating || isDefault}
                    className={`relative h-6 w-11 rounded-full transition-colors ${
                      pack.enabled ? "bg-blue-500" : "bg-slate-600"
                    } ${isDefault || isUpdating ? "opacity-50 cursor-not-allowed" : "hover:brightness-110"}`}
                  >
                    <div
                      className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-all ${
                        pack.enabled ? "left-[22px]" : "left-0.5"
                      }`}
                    />
                  </button>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-700/30 pt-3">
                <div className="flex gap-3">
                  <div className="flex flex-col">
                    <span className="text-[9px] uppercase tracking-tighter opacity-40" style={{ color: "var(--th-text-secondary)" }}>
                      {t({ ko: "QA 규칙", en: "QA Rules", ja: "QA ルール", zh: "QA 规则" })}
                    </span>
                    <span className="text-[11px] font-medium" style={{ color: "var(--th-text-primary)" }}>
                      {Object.keys(pack.qa_rules || {}).length}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[9px] uppercase tracking-tighter opacity-40" style={{ color: "var(--th-text-secondary)" }}>
                      {t({ ko: "입력 항목", en: "Inputs", ja: "入力項目", zh: "输入项" })}
                    </span>
                    <span className="text-[11px] font-medium" style={{ color: "var(--th-text-primary)" }}>
                      {(pack.input_schema as any)?.required?.length || 0}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[9px] uppercase tracking-tighter opacity-40" style={{ color: "var(--th-text-secondary)" }}>
                      {t({ ko: "라우팅 힌트", en: "Routing", ja: "ルーティング", zh: "路由" })}
                    </span>
                    <span className="text-[11px] font-medium" style={{ color: "var(--th-text-primary)" }}>
                      {(pack.routing_keywords as any)?.length || 0}
                    </span>
                  </div>
                </div>

                {!isDefault && pack.enabled && (
                  <button
                    onClick={() => handleSetDefaultPack(pack.key)}
                    className="rounded-lg bg-blue-600/10 hover:bg-blue-600/20 px-3 py-1.5 text-[11px] font-bold text-blue-400 transition-colors border border-blue-500/20"
                  >
                    {t({ ko: "기본값으로 설정", en: "Set as Default", ja: "デフォルトに設定", zh: "设为默认" })}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
