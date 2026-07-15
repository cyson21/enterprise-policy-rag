import type { ComponentType } from "react";

import type { Persona } from "../../fixtures/personas";
import type { RouteId } from "../../app/routes";
import { routes } from "../../app/routes";
import { formatAuthMode, formatEnvironment, formatProvider, formatWorkspaceName } from "../../utils/display";
import { PersonaSelector } from "../persona/PersonaSelector";

type AppShellProps = {
  activeRoute: RouteId;
  activePersonaId: string;
  personas: Persona[];
  workspaceId: string;
  workspaceName: string;
  environment: string;
  provider: string;
  authMode: string;
  onRouteChange: (routeId: RouteId) => void;
  onPersonaChange: (personaId: string) => void;
};

export function AppShell({
  activeRoute,
  activePersonaId,
  personas,
  workspaceId,
  workspaceName,
  environment,
  provider,
  authMode,
  onRouteChange,
  onPersonaChange,
}: AppShellProps) {
  // 현재 라우트 id로 페이지 컴포넌트를 찾아 렌더하고, 없으면 첫 번째 라우트로 fallback한다.
  const route = routes.find((item) => item.id === activeRoute) ?? routes[0];
  const Page = route.element as ComponentType<PageProps>;
  // URL에서 전달된 persona id가 유효하지 않을 때의 방어적인 선택값이다.
  const activePersona = personas.find((persona) => persona.id === activePersonaId) ?? personas[0];

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="주요 내비게이션">
        <div className="brand-block">
          <span className="brand-mark">EP</span>
          <div>
            <strong>Enterprise Policy RAG</strong>
            <span>{formatWorkspaceName(workspaceName)}</span>
          </div>
        </div>

        <nav className="nav-list">
          {/* 라우트 배열 순서가 그대로 사이드바 버튼 순서이므로 화면 정합성 점검 포인트다. */}
          {routes.map((item) => {
            const Icon = item.icon;
            const selected = item.id === activeRoute;
            return (
              <button
                key={item.id}
                type="button"
                className={selected ? "nav-item is-active" : "nav-item"}
                onClick={() => onRouteChange(item.id)}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="workspace">
        <header className="top-bar">
          <div>
            <span className="eyebrow">{route.label}</span>
            <h1>{route.description}</h1>
          </div>
          <div className="top-actions">
            <span className="status-pill">{formatEnvironment(environment)}</span>
            <span className="status-pill provider">{formatProvider(provider)}</span>
            <span className="status-pill auth">권한 세션: {formatAuthMode(authMode)}</span>
            <PersonaSelector personas={personas} activePersonaId={activePersonaId} onChange={onPersonaChange} />
          </div>
        </header>

        <main className="page-surface">
          <Page workspaceId={workspaceId} activePersona={activePersona} />
        </main>
      </div>
    </div>
  );
}

export type PageProps = {
  workspaceId: string;
  activePersona: Persona;
};
