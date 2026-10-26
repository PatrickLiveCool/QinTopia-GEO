import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { resolve, relative, extname, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(root, "out");
const cases = JSON.parse(readFileSync(resolve(root, "content/cases.json"), "utf8"));
const routes = ["/", "/capabilities/", "/cases/", "/cooperation/", ...cases.map(({ slug }) => `/cases/${slug}/`)];

function walk(folder) {
  return readdirSync(folder, { withFileTypes: true }).flatMap((entry) => entry.isDirectory() ? walk(resolve(folder, entry.name)) : [resolve(folder, entry.name)]);
}

function localFile(url) {
  const path = decodeURIComponent(url.pathname);
  return resolve(output, `.${path}`, path.endsWith("/") ? "index.html" : "");
}

for (const route of routes) {
  const file = localFile(new URL(route, "https://fde.qintopia.cn"));
  assert(existsSync(file), `Missing directly accessible page: ${route}`);
}

const pages = walk(output).filter((file) => extname(file) === ".html");
for (const file of pages) {
  const html = readFileSync(file, "utf8");
  const page = relative(output, file);
  assert.match(html, /<html[^>]+lang="zh-CN"/, `Language missing: ${page}`);
  assert.match(html, /<meta\s+name="robots"\s+content="[^"]*noindex/, `Search exclusion missing: ${page}`);
  assert(!/千问办公|西安交通大学|New API|\/Users\/feather\/|方案注释|结构预览/.test(html), `Private or proposal-only content leaked into ${page}`);

  const route = page.endsWith("index.html") ? `/${page.slice(0, -10)}` : `/${page}`;
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1].replaceAll("&amp;", "&");
    if (!href || /^(?:data:|mailto:|tel:|javascript:)/.test(href)) continue;
    const url = new URL(href, `https://fde.qintopia.cn${route}`);
    if (url.origin !== "https://fde.qintopia.cn") continue;
    assert(existsSync(localFile(url)), `Broken local resource in ${page}: ${href}`);
  }
}

for (const item of cases) {
  const html = readFileSync(localFile(new URL(`/cases/${item.slug}/`, "https://fde.qintopia.cn")), "utf8");
  assert(html.includes(item.title), `Case title is not in the exported document: ${item.slug}`);
  for (const section of item.sections) {
    // Verify the full case is readable in the initial HTML, including without client JS.
    for (const block of section.blocks) for (const paragraph of block.items) {
      const plain = paragraph.replaceAll("**", "");
      const escaped = plain.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#x27;");
      assert(html.replace(/<[^>]*>/g, "").includes(escaped), `Missing case content in ${item.slug}: ${plain.slice(0, 36)}`);
    }
  }
}

console.log(`Verified ${routes.length} shareable routes, ${pages.length} HTML documents, local references, noindex, and full case content.`);
