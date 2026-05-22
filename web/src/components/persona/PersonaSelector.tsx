import type { Persona } from "../../fixtures/personas";
import { formatDepartmentIds, formatUserName } from "../../utils/display";

type PersonaSelectorProps = {
  personas: Persona[];
  activePersonaId: string;
  onChange: (personaId: string) => void;
};

export function PersonaSelector({ personas, activePersonaId, onChange }: PersonaSelectorProps) {
  const activePersona = personas.find((persona) => persona.id === activePersonaId) ?? personas[0];

  return (
    <label className="persona-selector">
      <span>사용자</span>
      <select value={activePersona.id} onChange={(event) => onChange(event.target.value)}>
        {personas.map((persona) => (
          <option key={persona.id} value={persona.id}>
            {formatUserName(persona.id, persona.displayName)} / {formatDepartmentIds(persona.departmentIds)}
          </option>
        ))}
      </select>
    </label>
  );
}
