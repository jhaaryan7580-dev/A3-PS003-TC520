import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "client/src") } },
  root: path.resolve(import.meta.dirname, "client"),
  publicDir: path.resolve(import.meta.dirname, "client/public"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
  },
  server: {
    host: true,
    allowedHosts: [
      ".manus.computer",
      ".manuspre.computer",
      ".manus-asia.computer",
      "localhost",
      "127.0.0.1",
    ],
  },
});
