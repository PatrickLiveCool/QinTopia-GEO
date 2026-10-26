export function InlineText({ children }: { children: string }) {
  return <>{children.split(/(\*\*.*?\*\*)/g).map((part, index) => part.startsWith("**") && part.endsWith("**") ? <strong key={index}>{part.slice(2, -2)}</strong> : part)}</>;
}
