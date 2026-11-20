interface PlaceholderPageProps {
  title: string
  phase: string
}

export function PlaceholderPage({ title, phase }: PlaceholderPageProps) {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-leaf-700">{title}</h1>
      <p className="mt-2 text-sm text-soil-500">
        Not implemented yet — scheduled for {phase}. See STATUS.md for the current checklist.
      </p>
    </div>
  )
}
