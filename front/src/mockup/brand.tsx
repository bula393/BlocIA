export function Brand({ compact = false, light = false }: { compact?: boolean; light?: boolean }) {
  return <span className={`mk-brand${light ? ' mk-brand--light' : ''}`}>
    <svg viewBox="0 0 40 40" role="img" aria-label="Logo de BloqIA"><path fill="currentColor" d="M4 4h19v13H4zM17 23h19v13H17zM4 23h7v13H4zM29 4h7v13h-7z" /></svg>
    {!compact && <span>bloq<span className="mk-brand-ia">ia</span><span className="mk-brand-period">.</span></span>}
  </span>;
}

const paths: Record<string, React.ReactNode> = {
  arrow: <><path d="M4 12h15M13 5l7 7-7 7" /></>,
  'arrow-up': <><path d="M5 19 19 5M5 5h14v14" /></>,
  down: <><path d="M12 4v16M5 13l7 7 7-7" /></>,
  chat: <><path d="M4 4h16v12H9l-5 4V4Z" /><path d="M8 8h8M8 12h5" /></>,
  history: <><path d="M4 9a8 8 0 1 1 0 7M4 4v5h5M12 8v5l3 2" /></>,
  profile: <><circle cx="12" cy="8" r="3.5" /><path d="M4 21v-2a8 8 0 0 1 16 0v2" /></>,
  user: <><circle cx="12" cy="8" r="3.5" /><path d="M4 21v-2a8 8 0 0 1 16 0v2" /></>,
  providers: <><path d="M4 7h16M4 17h16M8 4v6M16 14v6" /></>,
  settings: <><path d="M4 7h16M4 17h16M8 4v6M16 14v6" /></>,
  usage: <><path d="M4 20V4M4 20h17M8 16v-5M13 16V6M18 16V9" /></>,
  chart: <><path d="M4 20V4M4 20h17M8 16v-5M13 16V6M18 16V9" /></>,
  plus: <><path d="M12 5v14M5 12h14" /></>,
  close: <><path d="m6 6 12 12M18 6 6 18" /></>,
  x: <><path d="m6 6 12 12M18 6 6 18" /></>,
  menu: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
  check: <><path d="m5 12 4 4L19 6" /></>,
  chevron: <><path d="m8 5 7 7-7 7" /></>,
  'chevron-down': <><path d="m5 9 7 7 7-7" /></>,
  send: <><path d="m4 12 16-8-6 16-3-7-7-1ZM11 13l9-9" /></>,
  trash: <><path d="M4 6h16M9 6V3h6v3M7 6l1 14h8l1-14M10 10v6M14 10v6" /></>,
  logout: <><path d="M10 4H4v16h6M9 12h12M16 7l5 5-5 5" /></>,
  home: <><path d="m3 10 9-7 9 7M6 8v12h12V8M10 20v-7h4v7" /></>,
  lock: <><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" /></>,
  eye: <><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" /></>,
  refresh: <><path d="M20 8a8 8 0 0 0-14-3L3 8M3 3v5h5M4 16a8 8 0 0 0 14 3l3-3M16 16h5v5" /></>,
  external: <><path d="M14 3h7v7M21 3l-9 9M10 4H4v16h16v-6" /></>,
  shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" /><path d="m8 12 3 3 5-6" /></>,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v6M12 7v.1" /></>,
  alert: <><path d="m12 3 10 18H2L12 3ZM12 9v5M12 17v.1" /></>,
  globe: <><circle cx="12" cy="12" r="9" /><ellipse cx="12" cy="12" rx="4" ry="9" /><path d="M3 12h18" /></>,
  cpu: <><rect x="6" y="6" width="12" height="12" rx="2" /><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4" /></>,
  key: <><circle cx="8" cy="8" r="5" /><path d="m12 12 9 9M16 16l3-3M18 18l3-3" /></>,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 6 9 7 9-7" /></>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
  activity: <><path d="M3 12h4l3-8 4 16 3-8h4" /></>,
  minus: <><path d="M5 12h14" /></>,
  layers: <><path d="m3 8 9-5 9 5-9 5-9-5ZM3 12l9 5 9-5M3 16l9 5 9-5" /></>,
  search: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 5 5" /></>,
  'arrow-right': <><path d="M4 12h15M13 5l7 7-7 7" /></>,
  'arrow-left': <><path d="M20 12H5M11 5l-7 7 7 7" /></>,
  'arrow-up-right': <><path d="M5 19 19 5M5 5h14v14" /></>,
  'chevron-right': <><path d="m8 5 7 7-7 7" /></>,
  'log-out': <><path d="M10 4H4v16h6M9 12h12M16 7l5 5-5 5" /></>,
  'eye-off': <><path d="m3 3 18 18M10 5a10 10 0 0 1 2 0c6.5 0 10 7 10 7a19 19 0 0 1-3 4M6 6c-2.6 2.2-4 6-4 6s3.5 7 10 7c2 0 3.6-.6 5-1.5" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M7 3v5M17 3v5M3 11h18M7 15h2M15 15h2" /></>,
};

export function Icon({ name, size = 20 }: { name: string; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.arrow}</svg>;
}
