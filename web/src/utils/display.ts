const departmentLabels: Record<string, string> = {
  security: "보안",
  finance: "재무",
  people: "인사",
  platform: "플랫폼",
};

// 표시용 텍스트 사전은 API 영문 id를 운영 화면에서 읽기 쉬운 형태로 변환한다.
const userLabels: Record<string, string> = {
  "mina-security": "김민아",
  "joon-finance": "박준",
  "hana-people": "이하나",
  "admin-platform": "최서진",
};

const documentLabels: Record<string, string> = {
  "Remote Access Policy": "원격 접속 정책",
  "Security Incident Manual": "보안 사고 대응 매뉴얼",
  "Finance Reimbursement Policy": "경비 정산 정책",
  "Executive Access Exception": "임원 접근 예외 정책",
};

// 화면 표시 레이블이 바뀌어도 매핑을 통해 일괄 관리한다.
const documentIdLabels: Record<string, string> = {
  doc_1: "원격 접속 정책",
  doc_2: "보안 사고 대응 매뉴얼",
  doc_3: "경비 정산 정책",
  doc_4: "임원 접근 예외 정책",
  "demo-security-doc": "보안 사고 대응 매뉴얼",
  "demo-finance-doc": "경비 정산 정책",
};

const queryLabels: Record<string, string> = {
  "security incident evidence": "보안 사고 증거 보존",
  "meal reimbursement receipt": "식대 정산 영수증",
};

// workspace/environment/provider/auth_mode 값은 영문 코드에서 한국어 라벨로 매핑한다.
export function formatWorkspaceName(value: string) {
  return value === "ACME Enterprise" ? "ACME 엔터프라이즈" : value;
}

export function formatEnvironment(value: string) {
  if (value === "local-demo") {
    return "로컬 데모";
  }
  if (value === "public-demo") {
    return "공개 데모";
  }
  return value;
}

export function formatProvider(value: string) {
  if (value === "fake" || value === "fake provider") {
    return "fake 제공자";
  }
  return value;
}

export function formatAuthMode(value: string) {
  if (value === "demo") {
    return "데모";
  }
  if (value === "trusted_headers") {
    return "SSO 헤더";
  }
  return value;
}

export function formatUserName(userId: string, fallback?: string) {
  return userLabels[userId] ?? fallback ?? userId;
}

export function formatDepartmentIds(departmentIds: string[]) {
  if (!departmentIds.length) {
    return "없음";
  }
  return departmentIds.map((departmentId) => departmentLabels[departmentId] ?? departmentId).join(", ");
}

export function formatVisibility(value: string) {
  if (value === "public") {
    return "전체 공개";
  }
  if (value === "department") {
    return "부서 한정";
  }
  if (value === "private") {
    return "비공개";
  }
  return value;
}

export function formatIndexingStatus(value: string) {
  if (value === "queued") {
    return "대기";
  }
  if (value === "indexing") {
    return "인덱싱 중";
  }
  if (value === "ready") {
    return "준비 완료";
  }
  if (value === "failed") {
    return "실패";
  }
  return value;
}

export function formatAccessReason(value: string) {
  if (value === "owner") {
    return "소유자";
  }
  if (value === "public") {
    return "전체 공개";
  }
  if (value === "department_match") {
    return "부서 일치";
  }
  return value;
}

export function formatDocumentTitle(title: string) {
  return documentLabels[title] ?? title;
}

export function formatDocumentId(documentId: string) {
  return documentIdLabels[documentId] ?? documentId;
}

export function formatDocumentIds(documentIds: string[]) {
  if (!documentIds.length) {
    return "없음";
  }
  return documentIds.map(formatDocumentId).join(", ");
}

export function formatQuery(value: string) {
  return queryLabels[value] ?? value;
}

export function formatMode(value: string) {
  if (value === "retrieval") {
    return "검색";
  }
  if (value === "answer") {
    return "답변";
  }
  return value;
}

export function formatRefusalReason(value: string | null | undefined) {
  if (!value) {
    return "없음";
  }
  if (value === "insufficient_evidence") {
    return "근거 부족";
  }
  return value;
}

export function formatSourceUri(value: string | null | undefined) {
  // 백엔드에 원본 URI가 없을 때도 사용자에게 빈칸이 아닌 기본 문구를 보여주기 위한 안전장치.
  return value ?? "로컬 문서";
}
