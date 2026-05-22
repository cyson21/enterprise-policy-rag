export type Persona = {
  id: string;
  displayName: string;
  departmentIds: string[];
  role: "employee" | "admin";
};

export type ApiPersona = {
  id: string;
  display_name: string;
  department_ids: string[];
  role: "employee" | "admin";
};

export const workspace = {
  id: "acme",
  name: "ACME Enterprise",
  environment: "local-demo",
  provider: "fake",
};

export const personas: Persona[] = [
  {
    id: "mina-security",
    displayName: "Mina Kim",
    departmentIds: ["security"],
    role: "employee",
  },
  {
    id: "joon-finance",
    displayName: "Joon Park",
    departmentIds: ["finance"],
    role: "employee",
  },
  {
    id: "hana-people",
    displayName: "Hana Lee",
    departmentIds: ["people"],
    role: "employee",
  },
  {
    id: "admin-platform",
    displayName: "Admin Choi",
    departmentIds: ["platform"],
    role: "admin",
  },
];

export function normalizePersona(persona: ApiPersona): Persona {
  return {
    id: persona.id,
    displayName: persona.display_name,
    departmentIds: persona.department_ids,
    role: persona.role,
  };
}
