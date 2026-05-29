import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// 프런트 개발 서버 설정과 API 프록시 경로를 한 곳에서 관리한다.
export default defineConfig({
  plugins: [react()],
  server: {
    // 프론트 기본 포트/바인딩은 로컬에서 충돌이 적은 5173, 127.0.0.1 고정이다.
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        // 정적 페이지에서 호출한 /api/<path>를 백엔드 루트 path로 치환한다.
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
