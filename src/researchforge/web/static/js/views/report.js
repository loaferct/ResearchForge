import { h, S } from "../core.js";

export default async function report() {
  const name = encodeURIComponent(S.project);
  return [h("h2", {}, "Final report"),
    h("p", { class: "lede" }, "Generated from the recorded data only; no model writes it. ",
      h("a", { href: `/api/projects/${name}/report.html?refresh=true`, target: "_blank" }, "Open in a new tab"), " or download the ",
      h("a", { href: `/api/projects/${name}/report.md?refresh=true`, download: `${S.project}-report.md` }, "Markdown version"), "."),
    h("iframe", { class: "report", src: `/api/projects/${name}/report.html?refresh=true`, sandbox: "", title: "Final report" })];
}
