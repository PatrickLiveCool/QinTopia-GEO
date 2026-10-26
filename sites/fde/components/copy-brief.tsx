"use client";

import { useState } from "react";

export function CopyBrief({ value }: { value: string }) {
  const [status, setStatus] = useState<"idle" | "copied" | "manual">("idle");
  async function copy() {
    try {
      if (!navigator.clipboard) throw new Error("Clipboard is unavailable");
      await navigator.clipboard.writeText(value);
      setStatus("copied");
    } catch {
      setStatus("manual");
    }
  }
  return <div className="copy-brief"><button type="button" className="button button-primary" onClick={copy}>{status === "copied" ? "已复制沟通提纲" : "复制项目沟通提纲"}</button><p role="status" aria-live="polite">{status === "copied" ? "已复制，可以补充项目情况后用于沟通。" : status === "manual" ? "浏览器未允许自动复制，可展开下方提纲手动复制。" : "将目标、系统和协作条件整理到同一份提纲中。"}</p><details open={status === "manual" || undefined}><summary>查看沟通提纲</summary><pre tabIndex={0}>{value}</pre></details></div>;
}
