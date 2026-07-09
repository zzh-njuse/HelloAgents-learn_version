import {
  Activity,
  Archive,
  CheckCircle2,
  Database,
  FolderPlus,
  HardDrive,
  Loader2,
  Plus,
  RefreshCw,
  Server,
  TriangleAlert
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import {
  createWorkspace,
  fetchReadiness,
  fetchSystemInfo,
  fetchWorkspaces,
  Readiness,
  SystemInfo,
  Workspace
} from "../lib/api";

type LoadState = "idle" | "loading" | "ready" | "error";

export function App() {
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | null>(null);
  const [workspaceName, setWorkspaceName] = useState("");
  const [workspaceDescription, setWorkspaceDescription] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [formState, setFormState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const selectedWorkspace = useMemo(
    () => workspaces.find((workspace) => workspace.id === selectedWorkspaceId) ?? null,
    [workspaces, selectedWorkspaceId]
  );

  async function refresh(signal?: AbortSignal) {
    setLoadState("loading");
    setLoadError(null);
    try {
      const [nextReadiness, nextSystemInfo, nextWorkspaces] = await Promise.all([
        fetchReadiness(signal),
        fetchSystemInfo(signal),
        fetchWorkspaces(signal)
      ]);
      setReadiness(nextReadiness);
      setSystemInfo(nextSystemInfo);
      setWorkspaces(nextWorkspaces);
      if (!selectedWorkspaceId && nextWorkspaces.length > 0) {
        setSelectedWorkspaceId(nextWorkspaces[0].id);
      }
      setLoadState("ready");
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") {
        return;
      }
      setLoadError(caught instanceof Error ? caught.message : "无法连接后端 API");
      setLoadState("error");
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void refresh(controller.signal);
    return () => controller.abort();
  }, []);

  async function handleCreateWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedName = workspaceName.trim();
    if (!trimmedName) {
      setFormError("名称不能为空");
      return;
    }
    if (trimmedName.length > 120) {
      setFormError("名称不能超过 120 个字符");
      return;
    }

    setFormState("loading");
    setFormError(null);
    try {
      const workspace = await createWorkspace({
        name: trimmedName,
        description: workspaceDescription.trim() || null
      });
      const nextWorkspaces = [workspace, ...workspaces];
      setWorkspaces(nextWorkspaces);
      setSelectedWorkspaceId(workspace.id);
      setWorkspaceName("");
      setWorkspaceDescription("");
      setFormState("ready");
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "创建 workspace 失败");
      setFormState("error");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Workspace navigation">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <Archive size={20} />
          </div>
          <div>
            <strong>HelloAgents Learn</strong>
            <span>Self-host workspace</span>
          </div>
        </div>

        <nav className="workspace-list" aria-label="Workspaces">
          {workspaces.length === 0 ? (
            <div className="empty-nav">暂无 workspace</div>
          ) : (
            workspaces.map((workspace) => (
              <button
                className={workspace.id === selectedWorkspaceId ? "nav-item active" : "nav-item"}
                key={workspace.id}
                onClick={() => setSelectedWorkspaceId(workspace.id)}
                type="button"
              >
                <span>{workspace.name}</span>
                <small>{workspace.slug}</small>
              </button>
            ))
          )}
        </nav>
      </aside>

      <main className="workspace-main">
        <header className="topbar">
          <div>
            <h1>{selectedWorkspace ? selectedWorkspace.name : "平台工作台"}</h1>
            <p>
              {selectedWorkspace
                ? "当前阶段提供 self-host 基础设施和 workspace 入口。"
                : "创建一个 workspace，开始配置后续资料管线。"}
            </p>
          </div>
          <button className="icon-button" onClick={() => void refresh()} type="button">
            {loadState === "loading" ? <Loader2 className="spin" size={18} /> : <RefreshCw size={18} />}
            <span>刷新</span>
          </button>
        </header>

        {loadError ? (
          <div className="notice error" role="alert">
            <TriangleAlert size={18} />
            <span>{loadError}</span>
          </div>
        ) : null}

        <section className="status-grid" aria-label="System status">
          <StatusTile
            icon={<Server size={20} />}
            label="API"
            detail={loadState === "error" ? "不可用" : "已连接"}
            ok={loadState !== "error"}
          />
          <StatusTile
            icon={<Database size={20} />}
            label="Postgres"
            detail={readiness?.checks.postgres.detail ?? statusText(readiness?.checks.postgres.ok)}
            ok={readiness?.checks.postgres.ok}
          />
          <StatusTile
            icon={<Activity size={20} />}
            label="Qdrant"
            detail={readiness?.checks.qdrant.detail ?? statusText(readiness?.checks.qdrant.ok)}
            ok={readiness?.checks.qdrant.ok}
          />
          <StatusTile
            icon={<Server size={20} />}
            label="Redis"
            detail={readiness?.checks.redis.detail ?? statusText(readiness?.checks.redis.ok)}
            ok={readiness?.checks.redis.ok}
          />
          <StatusTile
            icon={<HardDrive size={20} />}
            label="Storage"
            detail={readiness?.checks.storage.path ?? statusText(readiness?.checks.storage.ok)}
            ok={readiness?.checks.storage.ok}
          />
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <h2>创建 Workspace</h2>
                <p>阶段 1 只建立平台入口，资料入口会在阶段 2 接入。</p>
              </div>
              <FolderPlus size={20} />
            </div>
            <form className="workspace-form" onSubmit={handleCreateWorkspace}>
              <label>
                名称
                <input
                  onChange={(event) => setWorkspaceName(event.target.value)}
                  placeholder="例如：算法复习"
                  value={workspaceName}
                />
              </label>
              <label>
                描述
                <textarea
                  onChange={(event) => setWorkspaceDescription(event.target.value)}
                  placeholder="可选"
                  value={workspaceDescription}
                />
              </label>
              {formError ? (
                <div className="form-error" role="alert">
                  {formError}
                </div>
              ) : null}
              <button className="primary-button" disabled={formState === "loading"} type="submit">
                {formState === "loading" ? <Loader2 className="spin" size={18} /> : <Plus size={18} />}
                <span>创建</span>
              </button>
            </form>
          </div>

          <div className="panel workspace-panel">
            <div className="panel-heading">
              <div>
                <h2>当前 Workspace</h2>
                <p>{workspaces.length} 个 workspace</p>
              </div>
              <Database size={20} />
            </div>
            {selectedWorkspace ? (
              <div className="workspace-detail">
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{selectedWorkspace.id}</dd>
                  </div>
                  <div>
                    <dt>Slug</dt>
                    <dd>{selectedWorkspace.slug}</dd>
                  </div>
                  <div>
                    <dt>Storage</dt>
                    <dd>{systemInfo?.storage.configured ? "已配置" : "未加载"}</dd>
                  </div>
                </dl>
                <div className="empty-state">
                  <Archive size={24} />
                  <p>资料库、章节和练习将在后续阶段接入。</p>
                </div>
              </div>
            ) : (
              <div className="empty-state tall">
                <Archive size={24} />
                <p>还没有 workspace。</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function StatusTile({
  icon,
  label,
  detail,
  ok
}: {
  icon: ReactNode;
  label: string;
  detail: string;
  ok?: boolean;
}) {
  const ready = Boolean(ok);
  return (
    <div className="status-tile">
      <div className={ready ? "status-icon ok" : "status-icon warn"}>{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{detail}</strong>
      </div>
      {ready ? <CheckCircle2 className="status-check" size={18} /> : <TriangleAlert className="status-warn" size={18} />}
    </div>
  );
}

function statusText(ok?: boolean) {
  if (ok === undefined) {
    return "未加载";
  }
  return ok ? "可用" : "不可用";
}
