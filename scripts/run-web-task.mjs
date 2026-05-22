import { spawn } from "node:child_process";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const webRoot = resolve(root, "web");
const task = process.argv[2];
const binExtension = process.platform === "win32" ? ".cmd" : "";

const tasks = {
  dev: () => run(webBin("vite"), ["--host", "127.0.0.1"], webRoot),
  build: async () => {
    await run(webBin("tsc"), ["-b"], webRoot);
    await run(webBin("vite"), ["build"], webRoot);
  },
  "build:static": async () => {
    const env = { VITE_DEMO_MODE: "static" };
    await run(webBin("tsc"), ["-b"], webRoot, env);
    await run(webBin("vite"), ["build"], webRoot, env);
  },
  "preview:static": () =>
    run(webBin("vite"), ["preview", "--host", "127.0.0.1", "--port", "4173", "--strictPort"], webRoot, {
      VITE_DEMO_MODE: "static",
    }),
  smoke: () => run(process.execPath, ["scripts/smoke.mjs"], webRoot),
};

if (!task || !tasks[task]) {
  console.error(`usage: node scripts/run-web-task.mjs ${Object.keys(tasks).join("|")}`);
  process.exit(2);
}

await tasks[task]();

function webBin(name) {
  return resolve(webRoot, "node_modules", ".bin", `${name}${binExtension}`);
}

function run(command, args, cwd, env = {}) {
  return new Promise((resolveRun, rejectRun) => {
    const child = spawn(command, args, {
      cwd,
      env: { ...process.env, ...env },
      stdio: "inherit",
    });
    child.on("error", rejectRun);
    child.on("exit", (code, signal) => {
      if (code === 0) {
        resolveRun();
        return;
      }
      rejectRun(new Error(`${command} ${args.join(" ")} failed with ${signal ?? code}`));
    });
  });
}
