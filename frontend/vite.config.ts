import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../src/pytuitor_web/static",
    emptyOutDir: true,
    chunkSizeWarningLimit: 1600,
  },
  test: { environment: "jsdom" },
});
