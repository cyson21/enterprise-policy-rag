import type { ComponentType } from "react";

import type { Persona } from "../../fixtures/personas";
import type { RouteId } from "../../app/routes";
import { routes } from "../../app/routes";
import { formatEnvironment, formatProvider, formatWorkspaceName } from "../../utils/display";
import { PersonaSelector } from "../persona/PersonaSelector";

type AppShellProps = {
  activeRoute: RouteId;
  activePersonaId: string;
  personas: Persona[];
  workspaceId: string;
  workspaceName: string;
  environment: string;
  provider: string;
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
  onRouteChange,
  onPersonaChange,
}: AppShellProps) {
  const route = routes.find((item) => item.id === activeRoute) ?? routes[0];
  const Page = route.element as ComponentType<PageProps>;
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
