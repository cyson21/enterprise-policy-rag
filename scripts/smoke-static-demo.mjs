import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { spawn } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const distRoot = resolve(root, "web", "dist");
const chromePath = findChromePath();
const requestedPaths = [];

if (!existsSync(resolve(distRoot, "index.html"))) {
  console.error("missing web/dist/index.html; run node scripts/run-web-task.mjs build:static first");
  process.exit(1);
}

if (!chromePath) {
  console.error("Google Chrome or Chromium was not found for static demo smoke");
  process.exit(1);
}

const server = createServer(async (request, response) => {
  const url = new URL(request.url ?? "/", "http://127.0.0.1");
  requestedPaths.push(url.pathname);

  try {
    const filePath = await resolveStaticPath(url.pathname);
    const body = await readFile(filePath);
    response.writeHead(200, { "Content-Type": contentType(filePath) });
    response.end(body);
  } catch {
    const body = await readFile(resolve(distRoot, "index.html"));
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(body);
  }
});

await new Promise((resolveListen) => server.listen(0, "127.0.0.1", resolveListen));
const address = server.address();
const port = typeof address === "object" && address ? address.port : 0;

try {
  const operationsDom = await dumpDom(`http://127.0.0.1:${port}/?route=operations`);
  const adminDom = await dumpDom(`http://127.0.0.1:${port}/?route=knowledge&persona=admin-platform`);
  const failures = [];

  for (const text of ["Enterprise Policy RAG", "공개 데모", "권한 세션", "운영 지표", "쿼리 상세", "평가 리포트"]) {
    if (!operationsDom.includes(text)) {
      failures.push(`missing rendered text: ${text}`);
    }
  }

  for (const text of ["지식 라이브러리", "관리 작업", "문서 업데이트", "문서 삭제", "감사 로그"]) {
    if (!adminDom.includes(text)) {
      failures.push(`missing admin rendered text: ${text}`);
    }
  }

  const apiRequests = requestedPaths.filter((path) => path.startsWith("/api"));
  if (apiRequests.length) {
    failures.push(`static demo made API requests: ${apiRequests.join(", ")}`);
  }

  if (failures.length) {
    console.error(failures.join("\n"));
    process.exitCode = 1;
  } else {
    console.log("static demo smoke passed");
  }
} finally {
  server.close();
}

async function resolveStaticPath(pathname) {
  const normalized = pathname === "/" ? "/index.html" : pathname;
  const filePath = resolve(join(distRoot, normalized));
  if (!filePath.startsWith(distRoot)) {
    throw new Error("invalid path");
  }
  return filePath;
}

function dumpDom(url) {
  return new Promise((resolveDump, rejectDump) => {
    const child = spawn(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--no-first-run",
      "--no-default-browser-check",
      "--virtual-time-budget=3000",
      "--dump-dom",
      url,
    ]);
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", rejectDump);
    child.on("exit", (code) => {
      if (code === 0) {
        resolveDump(stdout);
        return;
      }
      rejectDump(new Error(`Chrome exited with ${code}: ${stderr}`));
    });
  });
}

function findChromePath() {
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    process.env.CHROME_PATH,
  ].filter(Boolean);
  return candidates.find((candidate) => existsSync(candidate)) ?? null;
}

function contentType(filePath) {
  const extension = extname(filePath);
  if (extension === ".html") {
    return "text/html; charset=utf-8";
  }
  if (extension === ".js") {
    return "text/javascript; charset=utf-8";
  }
  if (extension === ".css") {
    return "text/css; charset=utf-8";
  }
  return "application/octet-stream";
}
