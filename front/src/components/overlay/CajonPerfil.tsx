import type { ReactNode } from 'react';

export function CajonPerfil({ children }: { children: ReactNode }) {
  return <aside className="bloq-drawer">{children}</aside>;
}
