import Link from "next/link";

export default function NotFound() {
  return <section className="container empty-state section"><p className="eyebrow">404 / PAGE NOT FOUND</p><h1>这个页面没有找到。</h1><p>可以返回案例目录，继续查找相关项目。</p><Link className="button button-primary" href="/cases/">查看项目案例</Link></section>;
}
