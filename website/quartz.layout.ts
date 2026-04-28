import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [
    Component.HomepageStats(),
    Component.HomepageRecent(),
    Component.HomepageTags(),
  ],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/Kendrick-Stein/MCISLAB_DeepRead",
    },
  }),
}

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.PaperMeta(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      folderDefaultState: "collapsed",
      useSavedState: false,
      mapFn: (node) => {
        if (!node.isFolder) {
          node.displayName = node.slugSegment
        }
      },
      sortFn: (a, b) => {
        const order = ["DomainMaps", "Papers", "Topics", "Ideas", "Projects"]
        const aIdx = order.indexOf(a.displayName)
        const bIdx = order.indexOf(b.displayName)
        if (aIdx !== -1 && bIdx !== -1) return aIdx - bIdx
        if (aIdx !== -1) return -1
        if (bIdx !== -1) return 1
        if (a.slug?.startsWith("Papers/") && b.slug?.startsWith("Papers/")) {
          return b.displayName.localeCompare(a.displayName)
        }
        return a.displayName.localeCompare(b.displayName)
      },
    }),
    Component.SidebarTags(),
  ],
  right: [
    Component.DesktopOnly(Component.TableOfContents()),
  ],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      folderDefaultState: "collapsed",
      useSavedState: false,
      mapFn: (node) => {
        if (!node.isFolder) {
          node.displayName = node.slugSegment
        }
      },
      sortFn: (a, b) => {
        const order = ["DomainMaps", "Papers", "Topics", "Ideas", "Projects"]
        const aIdx = order.indexOf(a.displayName)
        const bIdx = order.indexOf(b.displayName)
        if (aIdx !== -1 && bIdx !== -1) return aIdx - bIdx
        if (aIdx !== -1) return -1
        if (bIdx !== -1) return 1
        if (a.slug?.startsWith("Papers/") && b.slug?.startsWith("Papers/")) {
          return b.displayName.localeCompare(a.displayName)
        }
        return a.displayName.localeCompare(b.displayName)
      },
    }),
    Component.SidebarTags(),
  ],
  right: [],
}