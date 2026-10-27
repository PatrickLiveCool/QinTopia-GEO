"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentProps } from "react";

export function SiteLink({ href, ...props }: ComponentProps<typeof Link>) {
  const pathname = usePathname();
  const target = pathname.startsWith("/compare") && typeof href === "string" && href.startsWith("/") && !href.startsWith("/compare") ? `/compare${href}` : href;
  return <Link href={target} {...props} />;
}
