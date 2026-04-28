import { QuartzConfig } from "@jackyzha0/quartz"
import * as Plugin from "@jackyzha0/quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "DeepRead - AI Research Notebook",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    baseUrl: "https://kendrickstein.github.io/MCISLAB_DeepRead",
    ignorePatterns: ["private", "templates", ".obsidian", "Workbench"],
    defaultDatePublication: new Date("2024-04-01"),
    generateSocialImages: false,
    theme: {
      typography: {
        font: "sans-serif",
        headerFont: "serif",
        codeFont: "monospace",
      },
      colors: {
        lightMode: {
          light: "#faf8f5",
          lightgray: "#e5e5e5",
          gray: "#b8b8b8",
          darkgray: "#4e4e4e",
          dark: "#2b2b2b",
          secondary: "#284182",
          tertiary: "#84a84b",
          highlight: "#ffff1f",
        },
        darkMode: {
          light: "#1e1e2e",
          lightgray: "#2e2e3e",
          gray: "#4e4e5e",
          darkgray: "#bebebe",
          dark: "#dcdcdc",
          secondary: "#7b6a9e",
          tertiary: "#84a84b",
          highlight: "#ffff1f",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
      }),
      Plugin.ObsidianFlavoredMarkdown({
        comments: true,
        highlight: true,
      }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({
        renderMathInElementOptions: {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false}
          ]
        }
      }),
      Plugin.TableOfContents(),
      Plugin.HardBreaks(),
    ],
    filters: [
      Plugin.ExplicitPublish(),
    ],
    emitters: [
      Plugin.Intrinsics(),
      Plugin.ContentIndex({ enableSiteMap: true, enableRSS: true }),
      Plugin.StaticFolder(),
      Plugin.Pages(),
    ],
  },
}

export default config