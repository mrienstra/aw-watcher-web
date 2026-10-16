// Local A/B testing only (not for upstream): mirror console output to a log
// server on this machine (reference/log-sink.py), so logs are kept without
// DevTools open. Fire-and-forget: nothing awaits these requests.
const TAG = 'pr260'
const SINK = 'http://127.0.0.1:5699/log'
const MAX_LINE = 2000

function format(arg: unknown): string {
  if (typeof arg === 'string') return arg
  if (arg instanceof Error) return arg.stack ?? String(arg)
  try {
    return JSON.stringify(arg)
  } catch {
    return String(arg)
  }
}

for (const level of ['debug', 'info', 'warn', 'error'] as const) {
  const original = console[level].bind(console)
  console[level] = (...args: unknown[]) => {
    original(...args)
    const message = args.map(format).join(' ').slice(0, MAX_LINE)
    const line = `${new Date().toISOString()} ${TAG} ${level.toUpperCase()} ${message}`
    fetch(SINK, { method: 'POST', body: line }).catch(() => {})
  }
}

export {}
