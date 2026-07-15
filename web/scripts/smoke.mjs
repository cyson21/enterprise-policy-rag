import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");

// 필수 파일이 존재하는지 확인해 정적 데모 스크립트 실행 전 선검증한다.
const requiredFiles = [
  "package.json",
  "index.html",
  "src/app/App.tsx",
  "src/app/routes.tsx",
  "src/components/layout/AppShell.tsx",
  "src/components/persona/PersonaSelector.tsx",
  "src/fixtures/personas.ts",
  "src/routes/search/SearchPage.tsx",
  "src/routes/knowledge/KnowledgePage.tsx",
  "src/routes/retrieval-lab/RetrievalLabPage.tsx",
  "src/routes/operations/OperationsPage.tsx",
  "src/utils/display.ts",
  "src/styles/tokens.css",
];

const requiredLabels = [
  "검색 콘솔",
  "지식 라이브러리",
  "검색 실험실",
  "운영 지표",
  "ACME Enterprise",
  "fake 제공자",
  "공개 데모",
  "isStaticDemoMode",
  "김민아",
  "getAuthSession",
  "권한 세션",
  "loadRetrieval",
  "loadDocuments",
  "loadDocumentDetail",
  "접근 사유",
  "점수 기준",
  "문서 상세",
  "인덱싱 상태",
  "관리 작업",
  "문서 업데이트",
  "문서 삭제",
  "감사 로그",
  "loadAdminAuditLogs",
  "updateAdminDocument",
  "deleteAdminDocument",
  "임베딩 차원",
  "runLabRetrieval",
  "실험 쿼리",
  "activePersona",
  "thresholdControl",
  "loadOperationsSummary",
  "loadQueryTrend",
  "쿼리 추세",
  "loadQueryDetail",
  "쿼리 상세",
  "저장된 근거",
  "operations-console",
  "operations-detail-panel",
  "검색 적중률",
  "최근 쿼리",
  "loadTopEvidence",
  "주요 근거 문서",
  "loadAnswer",
  "근거 기반 답변",
  "거절 사유",
  "예상 비용",
  "loadEvalRuns",
  "인용 커버리지",
  "평가 리포트",
];

// 누락 항목이 하나라도 있으면 CI/로컬 스크립트가 빠르게 실패하도록 수집한다.
const failures = [];

for (const file of requiredFiles) {
  if (!existsSync(resolve(root, file))) {
    failures.push(`missing file: ${file}`);
  }
}

// 파일 목록 검증 후 화면 라벨 존재 여부를 함께 검사해 번역/표기 누락을 잡는다.
const searchable = requiredFiles
  .filter((file) => file.endsWith(".tsx") || file.endsWith(".ts") || file.endsWith(".css") || file.endsWith(".html"))
  .filter((file) => existsSync(resolve(root, file)))
  .map((file) => readFileSync(resolve(root, file), "utf8"))
  .join("\n");

for (const label of requiredLabels) {
  if (!searchable.includes(label)) {
    failures.push(`missing label: ${label}`);
  }
}

// 수집된 누락분은 에러로 종료해 smoke 스크립트의 실패 조건을 명시한다.
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("frontend shell smoke passed");
