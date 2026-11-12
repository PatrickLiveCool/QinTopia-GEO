import Link from "next/link";
import { site } from "@/content/site";
import { PixelIcon } from "./pixel-icon";
import { RevealText } from "./reveal-text";

export function AgenticFooter() {
  return <footer className="ag-footer"><div className="ag-footer-scene"><img src="/agentic/footer.png" alt="" loading="lazy" /><div className="ag-footer-copy"><PixelIcon type="integrations" size={40} /><span className="ag-tag">一起向前</span><RevealText className="ag-footer-title">{"从一个具体问题开始，\n让工作真正向前。"}</RevealText><Link className="ag-button" href="/cooperation/">了解合作方式 <span aria-hidden="true">↗</span></Link></div></div><div className="ag-footer-bottom"><div className="ag-wordmark">QINTOPIA<span>{site.name}</span></div><nav aria-label="页脚导航">{site.navigation.map(link => <Link href={link.href} key={link.href}>{link.label}</Link>)}</nav><span>AI 应用工程 · 生态协同交付</span></div></footer>;
}
