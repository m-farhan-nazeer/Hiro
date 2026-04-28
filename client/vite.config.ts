import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import dynamicImport from "vite-plugin-dynamic-import";

const ssr = process.env.SSR ? require("vite-plugin-ssr/plugin") : undefined;

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react({
            babel: {
                plugins: ["babel-plugin-macros"],
            },
        }),
        dynamicImport(),
        ssr ? ssr() : [],
    ].filter(Boolean),
    assetsInclude: ["**/*.md"],
    resolve: {
        alias: {
            "@": path.join(__dirname, "src"),
        },
    },
    build: {
        outDir: "dist",
    },
    server: {
        host: "0.0.0.0",
        port: 5000,
        allowedHosts: true,
    },
    preview: {
        host: "0.0.0.0",
        port: 5000,
        allowedHosts: true,
    },
});
