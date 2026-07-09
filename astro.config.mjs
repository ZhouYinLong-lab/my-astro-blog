import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import tailwind from "@astrojs/tailwind";
import playformCompress from "@playform/compress";
import terser from "@rollup/plugin-terser";
import { defineConfig } from "astro/config";
import expressiveCode from "astro-expressive-code";
import icon from "astro-icon";
import rehypeExternalLinks from "rehype-external-links";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

import { CODE_THEME, USER_SITE } from "./src/config.ts";

import updateConfig from "./src/integration/updateConfig.ts";

import { remarkReadingTime } from "./src/plugins/remark-reading-time";

import react from "@astrojs/react";

// https://astro.build/config
export default defineConfig({
  site: USER_SITE,
  output: "static",
  style: {
    scss: {
      includePaths: ["./src/styles"],
    },
  },
  integrations: [updateConfig(), expressiveCode({
    themes: [CODE_THEME],
    styleOverrides: {
      borderRadius: "0.75rem",
    },
  }), mdx(), icon(), terser({
    compress: true,
    mangle: true,
  }), sitemap(), tailwind({
    configFile: "./tailwind.config.mjs",
  }), playformCompress(), react()],
  markdown: {
    remarkPlugins: [remarkMath, remarkReadingTime],
    rehypePlugins: [
      rehypeKatex,
      [
        rehypeExternalLinks,
        {
          rel: "noopener noreferrer",
          content: { type: "text", value: "↗" },
        },
      ],
    ],
  },
  
  // Content Security Policy
  vite: {
    plugins: [
      {
        name: 'csp-headers',
        transformIndexHtml() {
          return [
            {
              tag: 'meta',
              attrs: {
                'http-equiv': 'Content-Security-Policy',
                content: [
                  "default-src 'self'",
                  "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.staticfile.net cdn.jsdelivr.net",
                  "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.staticfile.net",
                  "img-src 'self' data: https:",
                  "font-src 'self' fonts.gstatic.com cdn.staticfile.net",
                  "connect-src 'self' https:",
                  "frame-src 'self' https:",
                  "media-src 'self' https:",
                ].join('; '),
              },
            },
          ];
        },
      },
    ],
    css: {
      preprocessorOptions: {
        scss: {
          api: "modern-compiler",
        },
      },
    },
  },
});