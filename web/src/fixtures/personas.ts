export type Persona = {
  id: string;
  displayName: string;
  departmentIds: string[];
  role: "employee" | "admin";
};

// 서버 응답(Persona API)과 프런트 내부 Persona 스키마를 분리해 유지.
export type ApiPersona = {
  id: string;
  display_name: string;
  department_ids: string[];
  role: "employee" | "admin";
};

// 정적 데모에서 공유할 워크스페이스 기본값.
export const workspace = {
  id: "acme",
  name: "ACME Enterprise",
  environment: "local-demo",
  provider: "fake",
};

// 데모 persona 샘플: UI 상호작용 검증과 접근제어 분기 재현에 사용한다.
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

// 서버 응답 필드명을 내부 타입으로 정규화해 화면 조합 로직과 맞춘다.
export function normalizePersona(persona: ApiPersona): Persona {
  return {
    id: persona.id,
    displayName: persona.display_name,
    departmentIds: persona.department_ids,
    role: persona.role,
  };
}
