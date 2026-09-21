import type { CSSProperties } from 'react';

type MeterZone = 'safe' | 'attention' | 'limit';

export function MedidorTiempo({ value = 42, zone = 'safe' }: { value?: number; zone?: MeterZone }) {
  const boundedValue = Math.max(0, Math.min(100, value));
  return (
    <div className="bloq-meter" aria-label="Medidor de tiempo">
      <div className="bloq-meter__fill" data-zone={zone} style={{ '--meter-value': `${boundedValue}%` } as CSSProperties} />
    </div>
  );
}
