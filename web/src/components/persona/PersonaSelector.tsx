import type { Persona } from "../../fixtures/personas";
import { formatDepartmentIds, formatUserName } from "../../utils/display";

type PersonaSelectorProps = {
  personas: Persona[];
  activePersonaId: string;
  onChange: (personaId: string) => void;
};

export function PersonaSelector({ personas, activePersonaId, onChange }: PersonaSelectorProps) {
  // 페르소나 목록에서 id 미스매치가 나면 첫 항목으로 안전하게 복구한다.
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
