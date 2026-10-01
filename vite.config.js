import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    // Proxy API calls to FastAPI during development so you don't need CORS headers locally
    proxy: {
      "/books": "http://localhost:8000",
      "/upload": "http://localhost:8000",
      "/nlp": "http://localhost:8000",
      "/chat": "http://localhost:8000",
    },
  },
});