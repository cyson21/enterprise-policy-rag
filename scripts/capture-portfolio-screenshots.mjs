import { createServer } from "node:http";
import { readFile, rm, writeFile } from "node:fs/promises";
import { existsSync, mkdtempSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { spawn } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const distRoot = resolve(root, "web", "dist");
const assetRoot = resolve(root, "docs", "assets");
const chromePath = findChromePath();
const requestedPaths = [];

const captures = [
  {
    label: "operations desktop",
    route: "/?route=operations",
    output: "operations-demo-ko-v13-desktop.jpg",
    width: 1440,
    height: 1650,
    mobile: false,
    fullPage: false,
    waitFor: ["Enterprise Policy RAG", "운영 지표", "쿼리 상세", "평가 리포트"],
  },
  {
    label: "operations mobile webview",
    route: "/?route=operations",
    output: "operations-demo-ko-v13-mobile-overview.jpg",
    width: 500,
    height: 1400,
    mobile: true,
    fullPage: false,
    waitFor: ["Enterprise Policy RAG", "운영 지표", "쿼리 상세", "평가 리포트"],
  },
  {
    label: "operations mobile full page",
    route: "/?route=operations",
    output: "operations-demo-ko-v13-mobile-full-page.jpg",
    width: 500,
    height: 1500,
    mobile: true,
    fullPage: true,
    waitFor: ["Enterprise Policy RAG", "운영 지표", "주요 근거 문서", "평가 리포트"],
  },
  {
    label: "knowledge admin desktop",
    route: "/?route=knowledge&persona=admin-platform",
    output: "knowledge-admin-demo-ko-v1-desktop.jpg",
    width: 1440,
    height: 1350,
    mobile: false,
    fullPage: false,
    waitFor: ["Enterprise Policy RAG", "지식 라이브러리", "관리 작업", "문서 업데이트", "감사 로그"],
  },
];

async function main() {
  if (!existsSync(resolve(distRoot, "index.html"))) {
    console.error("missing web/dist/index.html; run node scripts/run-web-task.mjs build:static first");
    process.exit(1);
  }

  if (!chromePath) {
    console.error("Google Chrome or Chromium was not found for portfolio screenshot capture");
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
  let chrome = null;
  let client = null;

  try {
    chrome = await launchChrome();
    client = await CDPClient.connect(chrome.webSocketUrl);

    for (const capture of captures) {
      const result = await captureRoute(client, `http://127.0.0.1:${port}${capture.route}`, capture);
      console.log(
        [
          `captured ${capture.label}`,
          `file=${result.output}`,
          `viewport=${capture.width}x${capture.height}`,
          `image=${result.imageWidth}x${result.imageHeight}`,
          `scrollHeight=${result.scrollHeight}`,
        ].join(" "),
      );
    }

    const apiRequests = requestedPaths.filter((path) => path.startsWith("/api"));
    if (apiRequests.length) {
      throw new Error(`static screenshot capture made API requests: ${apiRequests.join(", ")}`);
    }

    console.log("portfolio screenshots captured");
  } finally {
    if (client) {
      await client.close();
    }
    if (chrome) {
      chrome.process.kill("SIGTERM");
      await rm(chrome.userDataDir, { recursive: true, force: true });
    }
    server.close();
  }
}

async function captureRoute(client, url, capture) {
  const { targetId } = await client.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await client.send("Target.attachToTarget", { targetId, flatten: true });
  const issues = [];

  client.onEvent((message) => {
    if (message.sessionId !== sessionId) {
      return;
    }
    if (message.method === "Runtime.exceptionThrown") {
      issues.push(`runtime exception: ${message.params?.exceptionDetails?.text ?? "unknown"}`);
    }
    if (message.method === "Log.entryAdded") {
      const entry = message.params?.entry;
      if (entry?.level === "error") {
        issues.push(`browser log error: ${entry.text}`);
      }
    }
  });

  await client.send("Page.enable", {}, sessionId);
  await client.send("Runtime.enable", {}, sessionId);
  await client.send("Log.enable", {}, sessionId);
  await setViewport(client, sessionId, capture.width, capture.height, capture.mobile);
  await client.send("Page.navigate", { url }, sessionId);
  await waitForRenderedPage(client, sessionId, capture.waitFor);

  const scrollHeight = await readNumber(client, sessionId, pageMetricExpression("scrollHeight"));
  const imageHeight = capture.fullPage ? Math.max(capture.height, Math.ceil(scrollHeight)) : capture.height;
  const imageWidth = capture.width;

  await setViewport(client, sessionId, imageWidth, imageHeight, capture.mobile);
  await waitForAnimationFrame(client, sessionId);

  const { data } = await client.send(
    "Page.captureScreenshot",
    {
      format: "jpeg",
      quality: 92,
      captureBeyondViewport: true,
      clip: {
        x: 0,
        y: 0,
        width: imageWidth,
        height: imageHeight,
        scale: 1,
      },
    },
    sessionId,
  );

  if (issues.length) {
    throw new Error(`${capture.label} reported browser issues:\n${issues.join("\n")}`);
  }

  const output = resolve(assetRoot, capture.output);
  await writeFile(output, Buffer.from(data, "base64"));
  await client.send("Target.closeTarget", { targetId });

  return {
    output: output.replace(`${root}/`, ""),
    imageWidth,
    imageHeight,
    scrollHeight,
  };
}

async function waitForRenderedPage(client, sessionId, waitFor) {
  const deadline = Date.now() + 7000;
  let lastText = "";

  while (Date.now() < deadline) {
    const value = await evaluate(client, sessionId, `({
      readyState: document.readyState,
      text: document.body ? document.body.innerText : "",
      title: document.title
    })`);
    lastText = value?.text ?? "";
    const isReady = value?.readyState === "complete" || value?.readyState === "interactive";
    const hasExpectedText = waitFor.every((text) => lastText.includes(text));
    const hasFrameworkOverlay =
      lastText.includes("Internal server error") ||
      lastText.includes("Failed to compile") ||
      lastText.includes("Vite Error");

    if (hasFrameworkOverlay) {
      throw new Error(`framework overlay text was rendered for ${waitFor.join(", ")}`);
    }

    if (isReady && hasExpectedText) {
      await waitForAnimationFrame(client, sessionId);
      return;
    }

    await delay(150);
  }

  throw new Error(`render timeout. Missing one of: ${waitFor.join(", ")}. Last text: ${lastText.slice(0, 400)}`);
}

async function waitForAnimationFrame(client, sessionId) {
  await evaluate(
    client,
    sessionId,
    "new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve(true))))",
    true,
  );
}

async function setViewport(client, sessionId, width, height, mobile) {
  await client.send(
    "Emulation.setDeviceMetricsOverride",
    {
      width,
      height,
      deviceScaleFactor: 1,
      mobile,
    },
    sessionId,
  );
}

async function readNumber(client, sessionId, expression) {
  const value = await evaluate(client, sessionId, expression);
  return Number.isFinite(value) ? value : 0;
}

function pageMetricExpression(metric) {
  return `Math.max(
    document.documentElement.${metric},
    document.body ? document.body.${metric} : 0
  )`;
}

async function evaluate(client, sessionId, expression, awaitPromise = false) {
  const response = await client.send(
    "Runtime.evaluate",
    {
      expression,
      awaitPromise,
      returnByValue: true,
    },
    sessionId,
  );
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.text ?? "Runtime.evaluate failed");
  }
  return response.result?.value;
}

async function resolveStaticPath(pathname) {
  const normalized = pathname === "/" ? "/index.html" : pathname;
  const filePath = resolve(join(distRoot, normalized));
  if (!filePath.startsWith(distRoot)) {
    throw new Error("invalid path");
  }
  return filePath;
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
  if (extension === ".svg") {
    return "image/svg+xml";
  }
  if (extension === ".jpg" || extension === ".jpeg") {
    return "image/jpeg";
  }
  if (extension === ".png") {
    return "image/png";
  }
  return "application/octet-stream";
}

function findChromePath() {
  const candidates = [
    process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ].filter(Boolean);
  return candidates.find((candidate) => existsSync(candidate)) ?? null;
}

async function launchChrome() {
  const userDataDir = mkdtempSync(join(tmpdir(), "enterprise-policy-rag-chrome-"));
  const child = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-debugging-port=0",
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ]);

  let stderr = "";
  const webSocketUrl = await new Promise((resolveSocket, rejectSocket) => {
    const timeout = setTimeout(() => {
      rejectSocket(new Error(`Chrome DevTools endpoint was not emitted. stderr: ${stderr}`));
    }, 7000);

    child.stderr.on("data", (chunk) => {
      stderr += chunk;
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timeout);
        resolveSocket(match[1]);
      }
    });

    child.on("error", (error) => {
      clearTimeout(timeout);
      rejectSocket(error);
    });

    child.on("exit", (code, signal) => {
      clearTimeout(timeout);
      rejectSocket(new Error(`Chrome exited early with ${signal ?? code}: ${stderr}`));
    });
  });

  return { process: child, userDataDir, webSocketUrl };
}

class CDPClient {
  constructor(webSocketUrl) {
    this.webSocket = new WebSocket(webSocketUrl);
    this.pending = new Map();
    this.eventHandlers = [];
    this.nextId = 1;
  }

  static async connect(webSocketUrl) {
    const client = new CDPClient(webSocketUrl);
    await new Promise((resolveOpen, rejectOpen) => {
      client.webSocket.addEventListener("open", resolveOpen, { once: true });
      client.webSocket.addEventListener("error", rejectOpen, { once: true });
    });

    client.webSocket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data.toString());
      if (message.id && client.pending.has(message.id)) {
        const { resolveCommand, rejectCommand } = client.pending.get(message.id);
        client.pending.delete(message.id);
        if (message.error) {
          rejectCommand(new Error(`${message.error.message}: ${message.error.data ?? ""}`));
        } else {
          resolveCommand(message.result ?? {});
        }
        return;
      }

      for (const handler of client.eventHandlers) {
        handler(message);
      }
    });

    return client;
  }

  send(method, params = {}, sessionId = undefined) {
    const id = this.nextId++;
    const payload = { id, method, params };
    if (sessionId) {
      payload.sessionId = sessionId;
    }

    const promise = new Promise((resolveCommand, rejectCommand) => {
      this.pending.set(id, { resolveCommand, rejectCommand });
    });
    this.webSocket.send(JSON.stringify(payload));
    return promise;
  }

  onEvent(handler) {
    this.eventHandlers.push(handler);
  }

  close() {
    return new Promise((resolveClose) => {
      if (this.webSocket.readyState === WebSocket.CLOSED) {
        resolveClose();
        return;
      }
      this.webSocket.addEventListener("close", resolveClose, { once: true });
      this.webSocket.close();
    });
  }
}

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

await main();
