"use client"

import { useEffect, useRef, useState } from "react"
import { useMotion } from "./motion-context"

// Splits text into words and reveals each with staggered opacity+blur+translateY
// matching the AGENTIC intro animation style.
export function RevealText({
  children,
  className = "",
  as: Tag = "h2",
  stagger = 80,       // ms between each word
  duration = 700,     // ms per word transition
  delay = 0,          // initial delay before first word
  threshold = 0.2,    // IntersectionObserver threshold
}: {
  children: string
  className?: string
  as?: "h1" | "h2" | "h3" | "p" | "span"
  stagger?: number
  duration?: number
  delay?: number
  threshold?: number
}) {
  const ref       = useRef<HTMLElement>(null)
  const [visible, setVisible] = useState(true)
  const { enabled } = useMotion()

  useEffect(() => {
    const el = ref.current
    if (!el || !enabled) { setVisible(true); return }
    if (el.getBoundingClientRect().top > innerHeight) setVisible(false)

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { threshold }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold, enabled])

  // Split on spaces but preserve line breaks (rendered via <br />)
  const parts = children.split(/(\n)/g)
  const words: { word: string; index: number }[] = []
  let wordIndex = 0
  parts.forEach((part) => {
    if (part === "\n") {
      words.push({ word: "\n", index: wordIndex++ })
    } else {
      const units = /[\u3400-\u9fff]/.test(part) ? Array.from(part) : part.split(/(?<=\s)/)
      units.forEach(word => words.push({ word, index: wordIndex++ }))
    }
  })

  const totalWords = words.filter(w => w.word !== "\n").length

  return (
    // @ts-ignore — dynamic tag
    <Tag ref={ref} aria-label={children.replace(/\n/g, "")} className={className} style={{ display: "block", overflow: "hidden" }}>
      {words.map(({ word, index }) => {
        if (word === "\n") return <br key={`br-${index}`} />

        const wordDelay = enabled ? delay + Math.min(index * Math.min(stagger, 30), 450) : 0

        return (
          <span
            key={index}
            aria-hidden="true"
            style={{
              display:    "inline-block",
              opacity:    visible ? 1 : 0,
              filter:     visible ? "blur(0px)" : "blur(8px)",
              transform:  visible ? "translateY(0)" : "translateY(12px)",
              transition: visible
                ? `opacity ${duration}ms cubic-bezier(0.16,1,0.3,1) ${wordDelay}ms,
                   filter  ${duration}ms cubic-bezier(0.16,1,0.3,1) ${wordDelay}ms,
                   transform ${duration}ms cubic-bezier(0.16,1,0.3,1) ${wordDelay}ms`
                : "none",
            }}
          >
            {word}
          </span>
        )
      })}
    </Tag>
  )
}
