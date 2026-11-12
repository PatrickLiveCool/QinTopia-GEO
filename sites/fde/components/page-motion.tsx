"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

export function PageMotion() {
  const pathname = usePathname();

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (preference.matches || !("IntersectionObserver" in window)) return;

    const targets = document.querySelectorAll<HTMLElement>(".section-heading, .scenario-panel, .delivery-grid > article, .cooperation-cta, .cooperation-models > article, .role-grid > article, .brief-panel");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08 });

    targets.forEach((target) => {
      target.classList.add("scroll-reveal");
      observer.observe(target);
    });

    const revealAll = () => {
      if (!preference.matches) return;
      observer.disconnect();
      targets.forEach((target) => target.classList.add("is-revealed"));
    };
    preference.addEventListener("change", revealAll);
    return () => {
      observer.disconnect();
      preference.removeEventListener("change", revealAll);
      targets.forEach((target) => target.classList.remove("scroll-reveal", "is-revealed"));
    };
  }, [pathname]);

  return null;
}
