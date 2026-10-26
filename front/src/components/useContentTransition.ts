import { useLayoutEffect, useRef, type RefObject } from 'react';
import { motionAllowed, motionTiming } from '../app/motion';

// A quiet, interruptible fallback for local content changes and older browsers.
export function useContentTransition(target: RefObject<HTMLElement | null>, contentKey: unknown, enabled = true) {
  const previous = useRef(contentKey);
  useLayoutEffect(() => {
    const changed = previous.current !== contentKey;
    previous.current = contentKey;
    const element = target.current;
    if (!element) return;
    if (!changed || !enabled || !element.animate || !motionAllowed()) { element.style.removeProperty('opacity'); return; }
    const initialOpacity = element.style.opacity ? Number(element.style.opacity) : .65;
    const animation = element.animate([{ opacity: initialOpacity }, { opacity: 1 }], motionTiming('route'));
    animation.onfinish = () => element.style.removeProperty('opacity');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const cancel = () => { animation.cancel(); element.style.removeProperty('opacity'); };
    reduced.addEventListener('change', cancel);
    document.addEventListener('keydown', cancel, { once: true });
    return () => {
      const opacity = animation.playState === 'running' ? getComputedStyle(element).opacity : '';
      animation.cancel();
      if (opacity) element.style.opacity = opacity;
      else element.style.removeProperty('opacity');
      reduced.removeEventListener('change', cancel);
      document.removeEventListener('keydown', cancel);
    };
  }, [target, contentKey, enabled]);
}
