import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";

import { getAuthSession, type AuthSession } from "../api/client";
import { AppShell } from "../components/layout/AppShell";
import { isStaticDemoMode } from "../config/demoMode";
import { personas, workspace } from "../fixtures/personas";
import type { RouteId } from "./routes";
import "../styles/tokens.css";

export function App() {
  // 라우트/페르소나는 URL 또는 기본값으로 초기화하고, 세션은 비동기로 채운다.
  const [activeRoute, setActiveRoute] = useState<RouteId>(getInitialRoute);
  const [activePersonaId, setActivePersonaId] = useState(getInitialPersonaId);
  const [authSession, setAuthSession] = useState<AuthSession | null>(null);

  // auth API 실패가 나더라도 앱 렌더를 막지 않고 기본 데모 모드로 fallback한다.
  useEffect(() => {
    let cancelled = false;
    getAuthSession().then((session) => {
      if (!cancelled) {
        setAuthSession(session);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppShell
      activeRoute={activeRoute}
      activePersonaId={activePersonaId}
      personas={personas}
      workspaceId={workspace.id}
      workspaceName={workspace.name}
      environment={isStaticDemoMode ? "public-demo" : workspace.environment}
      provider={workspace.provider}
      authMode={authSession?.auth_mode ?? "demo"}
      onRouteChange={setActiveRoute}
      onPersonaChange={setActivePersonaId}
    />
  );
}

function getInitialRoute(): RouteId {
  // URL 파라미터 route가 허용된 식별자일 때만 적용한다.
  if (typeof window === "undefined") {
    return "search";
  }
  const route = new URLSearchParams(window.location.search).get("route");
  if (route === "search" || route === "knowledge" || route === "retrieval-lab" || route === "operations") {
    return route;
  }
  return "search";
}

function getInitialPersonaId() {
  // 페르소나 쿼리는 지원 목록과 교차 검증 후 기본값으로 폴백한다.
  if (typeof window === "undefined") {
    return personas[0].id;
  }
  const personaId = new URLSearchParams(window.location.search).get("persona");
  return personaId && personas.some((persona) => persona.id === personaId) ? personaId : personas[0].id;
}

const root = document.getElementById("root");

if (root) {
  createRoot(root).render(<App />);
}
