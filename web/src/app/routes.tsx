import { BookOpen, Gauge, Search, SlidersHorizontal } from "lucide-react";

import { KnowledgePage } from "../routes/knowledge/KnowledgePage";
import { OperationsPage } from "../routes/operations/OperationsPage";
import { RetrievalLabPage } from "../routes/retrieval-lab/RetrievalLabPage";
import { SearchPage } from "../routes/search/SearchPage";

export const routes = [
  {
    id: "search",
    label: "검색 콘솔",
    description: "권한 내 문서를 검색하고 근거를 확인",
    icon: Search,
    element: SearchPage,
  },
  {
    id: "knowledge",
    label: "지식 라이브러리",
    description: "문서, 청크, 공개 범위 관리",
    icon: BookOpen,
    element: KnowledgePage,
  },
  {
    id: "retrieval-lab",
    label: "검색 실험실",
    description: "top-k, 점수 기준, 권한 필터 디버깅",
    icon: SlidersHorizontal,
    element: RetrievalLabPage,
  },
  {
    id: "operations",
    label: "운영 지표",
    description: "쿼리, 지연 시간, 비용, 평가 지표",
    icon: Gauge,
    element: OperationsPage,
  },
] as const;

export type RouteId = (typeof routes)[number]["id"];
