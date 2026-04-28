import { QuartzLayout } from "@jackyzha0/quartz"
import * as Component from "@jackyzha0/quartz/components"

const layout: QuartzLayout = {
  header: {
    title: "DeepRead",
    subtitle: "AI Research Notebook",
    links: [
      { title: "Papers", href: "/Papers" },
      { title: "Topics", href: "/Topics" },
      { title: "Ideas", href: "/Ideas" },
      { title: "Survey", href: "/Topics/GUIAgent-Survey" },
    ],
  },
  footer: {
    links: [
      { title: "GitHub", href: "https://github.com/kendrickstein/MCISLAB_DeepRead" },
    ],
    text: "Built with Quartz",
  },
  left: [
    Component.PageList(),
    Component.RecentNotes({ limit: 5 }),
  ],
  right: [
    Component.TableOfContents(),
    Component.Search(),
    Component.Darkmode(),
    Component.Backlinks(),
    Component.Tags(),
  ],
}

export default layout