import type { ReactNode } from 'react';

export function CajonPerfil({ children }: { children: ReactNode }) {
  return <aside className="bloq-drawer profile-summary" aria-label="Datos de tu cuenta">{children}</aside>;
}
