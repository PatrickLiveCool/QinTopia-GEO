import Link from "next/link";
import { site } from "@/content/site";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <div><p className="footer-name">{site.name}</p><p>AI 应用落地与生态协同交付</p></div>
        <div className="footer-links"><Link href="/capabilities/">服务能力</Link><Link href="/cases/">项目案例</Link><Link href="/cooperation/">合作方式</Link></div>
        <span className="mono footer-signature">QINTOPIA / FIELD DELIVERY</span>
      </div>
    </footer>
  );
}
