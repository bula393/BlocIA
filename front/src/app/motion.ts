type ViewChange = { skipTransition: () => void; ready: Promise<void>; finished: Promise<void> };
type TransitionDocument = Document & { startViewTransition?: (update: () => void) => ViewChange };
let activeTransition: ViewChange | undefined;
let navigationVersion = 0;

export function motionAllowed() {
  return document.documentElement.dataset.inputMethod !== 'keyboard'
    && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function motionTiming(kind: 'route' | 'disclosure') {
  const tokens = getComputedStyle(document.documentElement);
  return {
    duration: parseFloat(tokens.getPropertyValue(`--motion-${kind}`)) || (kind === 'route' ? 160 : 200),
    easing: tokens.getPropertyValue('--motion-ease-out').trim() || 'cubic-bezier(.23, 1, .32, 1)',
  };
}

export function cancelViewChange() {
  navigationVersion += 1;
  activeTransition?.skipTransition();
  activeTransition = undefined;
}

export function changeView(update: (synchronous: boolean) => void) {
  cancelViewChange();
  const version = navigationVersion;
  const start = (document as TransitionDocument).startViewTransition;
  if (!motionAllowed() || !start) { update(false); return; }
  const transition = start.call(document, () => {
    // Skipping a native transition still runs its callback. Ignore obsolete destinations.
    if (version === navigationVersion) update(true);
  });
  activeTransition = transition;
  void transition.ready.catch(() => undefined);
  void transition.finished.catch(() => undefined).then(() => {
    if (activeTransition === transition) activeTransition = undefined;
  });
}

export function trackMotionPreferences() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = () => { document.documentElement.dataset.inputMethod = 'pointer'; };
  const keyboard = () => {
    document.documentElement.dataset.inputMethod = 'keyboard';
    activeTransition?.skipTransition();
  };
  const preference = () => { if (reduced.matches) activeTransition?.skipTransition(); };
  document.addEventListener('pointerdown', pointer, true);
  document.addEventListener('keydown', keyboard, true);
  reduced.addEventListener('change', preference);
  return () => {
    cancelViewChange();
    document.removeEventListener('pointerdown', pointer, true);
    document.removeEventListener('keydown', keyboard, true);
    reduced.removeEventListener('change', preference);
    delete document.documentElement.dataset.inputMethod;
  };
}
