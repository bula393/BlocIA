import { useEffect } from 'react';
import type { UsageLock } from '../../api/chat';

/** Schedule against the server clock; re-arm on every successful refresh. */
export function useUsageLockRefresh(lock: UsageLock | undefined, updatedAt: number, refresh: () => Promise<unknown>) {
  useEffect(() => {
    if (!lock?.blocked || !lock.lockUntil) return;
    const unlockAt = Date.parse(lock.lockUntil);
    const serverNow = lock.serverTime ? Date.parse(lock.serverTime) : Date.now();
    if (!Number.isFinite(unlockAt) || !Number.isFinite(serverNow)) return;
    const elapsed = lock.serverTime ? Math.max(0, Date.now() - updatedAt) : 0;
    // Retry shortly if a response still reports a lock at its expiry boundary.
    const delay = Math.min(2_147_483_647, Math.max(1000, unlockAt - serverNow - elapsed + 100));
    const timer = window.setTimeout(() => void refresh(), delay);
    return () => window.clearTimeout(timer);
  }, [lock?.blocked, lock?.lockUntil, lock?.serverTime, updatedAt, refresh]);
}
