import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

import { fileURLToPath } from "node:url";
import path from "node:path";
import { env as processEnv } from "node:process";

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode, command }) => {
  const env = { ...loadEnv(mode, path.dirname(frontendRoot), ""), ...loadEnv(mode, frontendRoot, ""), ...processEnv };
  if (!env.VITE_API_BASE_URL) throw new Error("VITE_API_BASE_URL is required. Copy frontend/.env.example to frontend/.env and configure it.");
  if (command === "serve" && (!env.VITE_HOST || !env.VITE_PORT)) throw new Error("VITE_HOST and VITE_PORT are required in the frontend environment.");
  const port = Number(env.VITE_PORT);
  if (command === "serve" && (!Number.isInteger(port) || port < 1 || port > 65535)) throw new Error("VITE_PORT must be a valid port.");
  return {
    plugins: [react(), tailwindcss()],
    define: { "import.meta.env.VITE_API_BASE_URL": JSON.stringify(env.VITE_API_BASE_URL) },
    server: { host: env.VITE_HOST, port, strictPort: true },
    preview: { host: env.VITE_HOST, port, strictPort: true },
  };
});
