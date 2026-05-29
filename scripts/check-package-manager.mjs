import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

// 루트 패키지/워크스페이스/잠금 파일이 배포 스크립트의 선조건을 충족하는지 점검한다.
const root = resolve(import.meta.dirname, "..");
const failures = [];

function readJson(path) {
  return JSON.parse(readFileSync(resolve(root, path), "utf8"));
}

// packageManager, pnpm-workspace, lockfile 존재 여부는 CI와 로컬 재현성에 직접 영향.
if (!existsSync(resolve(root, "package.json"))) {
  failures.push("missing root package.json");
} else {
  const rootPackage = readJson("package.json");
  if (rootPackage.packageManager !== "pnpm@11.1.3") {
    failures.push(`expected packageManager pnpm@11.1.3, got ${rootPackage.packageManager ?? "undefined"}`);
  }
  if (rootPackage.private !== true) {
    failures.push("root package.json must be private");
  }
}

if (!existsSync(resolve(root, "pnpm-workspace.yaml"))) {
  failures.push("missing pnpm-workspace.yaml");
} else {
  const workspace = readFileSync(resolve(root, "pnpm-workspace.yaml"), "utf8");
  if (!workspace.includes("web")) {
    failures.push("pnpm-workspace.yaml must include web package");
  }
  if (!workspace.includes("allowBuilds:") || !workspace.includes("esbuild: true")) {
    failures.push("pnpm-workspace.yaml must allow esbuild build scripts");
  }
}

if (!existsSync(resolve(root, "pnpm-lock.yaml"))) {
  failures.push("missing pnpm-lock.yaml");
}

const webPackage = readJson("web/package.json");
const rootScripts = readJson("package.json").scripts ?? {};
// 정적 빌드/프리뷰/스모크 진입점이 빠지지 않도록 필수 스크립트 존재를 고정 점검한다.
for (const script of ["web:build:static", "web:preview:static", "web:smoke:static"]) {
  if (!rootScripts[script]) {
    failures.push(`root package missing ${script} script`);
  }
}

for (const script of ["dev", "build", "smoke"]) {
  if (!webPackage.scripts?.[script]) {
    failures.push(`web package missing ${script} script`);
  }
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("package manager check passed");
