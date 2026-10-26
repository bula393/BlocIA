import { useLayoutEffect, useRef, type ReactNode } from 'react';
import { motionAllowed, motionTiming } from '../app/motion';

export function AnimatedDisclosure({ open, id, children }: { open: boolean; id: string; children: ReactNode }) {
  const content = useRef<HTMLDivElement>(null);
  const previous = useRef(open);

  useLayoutEffect(() => {
    const element = content.current;
    if (!element) return;
    const changed = previous.current !== open;
    previous.current = open;
    const fromHeight = element.hidden ? 0 : element.getBoundingClientRect().height;
    const fromOpacity = element.hidden ? 0 : Number(getComputedStyle(element).opacity);
    element.inert = !open;
    function settle() {
      element!.hidden = !open;
      element!.style.removeProperty('height');
      element!.style.removeProperty('opacity');
    }
    if (!changed || !element.animate || !motionAllowed()) {
      settle();
      return;
    }
    element.hidden = false;
    element.style.removeProperty('height');
    const animation = element.animate([
      { height: `${fromHeight}px`, opacity: fromOpacity },
      { height: `${open ? element.scrollHeight : 0}px`, opacity: open ? 1 : 0 },
    ], { ...motionTiming('disclosure'), fill: 'both' });
    const finish = () => { animation.cancel(); settle(); };
    animation.onfinish = finish;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const onPreference = () => { if (reduced.matches) finish(); };
    reduced.addEventListener('change', onPreference);
    document.addEventListener('keydown', finish, { once: true });
    return () => {
      // Preserve the presentation values before cancellation so a reversal never jumps.
      const height = element.getBoundingClientRect().height;
      const opacity = getComputedStyle(element).opacity;
      animation.cancel();
      element.style.height = `${height}px`;
      element.style.opacity = opacity;
      reduced.removeEventListener('change', onPreference);
      document.removeEventListener('keydown', finish);
    };
  }, [open]);

  return <div ref={content} id={id} className="animated-disclosure">{children}</div>;
}
