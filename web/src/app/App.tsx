import { createRoot } from "react-dom/client";
import { useState } from "react";

import { AppShell } from "../components/layout/AppShell";
import { isStaticDemoMode } from "../config/demoMode";
import { personas, workspace } from "../fixtures/personas";
import type { RouteId } from "./routes";
import "../styles/tokens.css";

export function App() {
  const [activeRoute, setActiveRoute] = useState<RouteId>(getInitialRoute);
  const [activePersonaId, setActivePersonaId] = useState(getInitialPersonaId);

  return (
    <AppShell
      activeRoute={activeRoute}
      activePersonaId={activePersonaId}
      personas={personas}
      workspaceId={workspace.id}
      workspaceName={workspace.name}
      environment={isStaticDemoMode ? "public-demo" : workspace.environment}
      provider={workspace.provider}
      onRouteChange={setActiveRoute}
      onPersonaChange={setActivePersonaId}
    />
  );
}

function getInitialRoute(): RouteId {
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
