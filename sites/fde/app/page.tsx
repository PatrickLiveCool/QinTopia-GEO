import type { Metadata } from "next";
import { AgenticHero } from "@/components/agentic/hero";
import { AgenticHomeContent } from "@/components/agentic/home-content";

export const metadata: Metadata = { alternates: { canonical: "/" } };

export default function HomePage() {
  return <><AgenticHero /><AgenticHomeContent /></>;
}
