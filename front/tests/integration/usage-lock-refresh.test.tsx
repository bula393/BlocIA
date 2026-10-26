import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import type { UsageLock } from '../../src/api/chat';
import { useUsageLockRefresh } from '../../src/features/chat/useUsageLockRefresh';

const serverNow = Date.parse('2026-10-26T12:00:00Z');
const lock: UsageLock = {
  blocked: true, reasonCodes: ['personal_questions'],
  serverTime: new Date(serverNow).toISOString(),
  lockUntil: new Date(serverNow + 60_000).toISOString(),
  usageSeconds: 3, usageLimitSeconds: 10800, personalQuestions: 3, personalQuestionLimit: 3,
};

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); });

test.each([-3_600_000, 3_600_000])('refreshes after one minute with client clock offset %i', async (offset) => {
  vi.setSystemTime(serverNow + offset);
  const refresh = vi.fn().mockResolvedValue(undefined);
  renderHook(() => useUsageLockRefresh(lock, Date.now(), refresh));
  await act(async () => { await vi.advanceTimersByTimeAsync(60_000); });
  expect(refresh).not.toHaveBeenCalled();
  await act(async () => { await vi.advanceTimersByTimeAsync(100); });
  expect(refresh).toHaveBeenCalledTimes(1);
});

test('rechecks a still-blocked expiry response and cancels after unlocking', async () => {
  vi.setSystemTime(serverNow);
  const refresh = vi.fn().mockResolvedValue(undefined);
  const { rerender } = renderHook(({ value, updatedAt }) => useUsageLockRefresh(value, updatedAt, refresh), {
    initialProps: { value: lock, updatedAt: Date.now() },
  });
  await act(async () => { await vi.advanceTimersByTimeAsync(60_100); });
  expect(refresh).toHaveBeenCalledTimes(1);
  rerender({ value: { ...lock, serverTime: new Date(serverNow + 60_100).toISOString() }, updatedAt: Date.now() });
  await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
  expect(refresh).toHaveBeenCalledTimes(2);
  rerender({ value: { ...lock, blocked: false, lockUntil: null }, updatedAt: Date.now() });
  await act(async () => { await vi.advanceTimersByTimeAsync(60_000); });
  expect(refresh).toHaveBeenCalledTimes(2);
});

test('subtracts time already elapsed in the query cache', async () => {
  vi.setSystemTime(serverNow + 45_000);
  const refresh = vi.fn().mockResolvedValue(undefined);
  renderHook(() => useUsageLockRefresh(lock, serverNow, refresh));
  await act(async () => { await vi.advanceTimersByTimeAsync(15_100); });
  expect(refresh).toHaveBeenCalledTimes(1);
});
