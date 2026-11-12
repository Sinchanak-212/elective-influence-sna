import { AlertTriangle, Database, Loader2, Info } from 'lucide-react'

export function LoadingState({ message = 'Loading…' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-[#8892a4]">
      <Loader2 className="mb-3 h-8 w-8 animate-spin text-[#8b5cf6]" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-[#8892a4]">
      <AlertTriangle className="mb-3 h-8 w-8 text-red-400" />
      <p className="text-sm font-medium text-red-400">Error</p>
      <p className="mt-1 max-w-sm text-center text-xs">{message}</p>
    </div>
  )
}

export function DataUnavailableState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-[#8892a4]">
      <Database className="mb-3 h-8 w-8 text-[#6366f1]" />
      <p className="text-sm font-medium text-[#e2e8f0]">Research data not available</p>
      <p className="mt-2 max-w-sm text-center text-xs">
        Place <code className="rounded bg-[#2d3748] px-1 py-0.5 text-cyan-300">survey_responses_anonymized.csv</code> in <code className="rounded bg-[#2d3748] px-1 py-0.5 text-cyan-300">data/raw/</code> and restart the backend.
      </p>
    </div>
  )
}

export function EmptyState({ message = 'No data to display.' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-[#8892a4]">
      <Info className="mb-3 h-8 w-8 text-[#8892a4]" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

export function InterpretationNote({ note }: { note: string }) {
  return (
    <div className="mt-4 flex gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
      <p className="text-xs text-amber-200/80">{note}</p>
    </div>
  )
}

export function UnverifiedNote({ note }: { note: string }) {
  return (
    <div className="mt-4 flex gap-2 rounded-lg border border-orange-500/20 bg-orange-500/5 p-3">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-orange-400" />
      <p className="text-xs text-orange-200/80">{note}</p>
    </div>
  )
}
