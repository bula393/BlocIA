import { useEffect, useLayoutEffect, useRef, useState, type PointerEvent, type RefObject } from 'react';

type SheetMotion = {
  settle: () => void;
  dismiss: (notify?: boolean) => void;
  grab: (event: PointerEvent<HTMLElement>) => void;
  drag: (event: PointerEvent<HTMLElement>) => void;
  release: (event: PointerEvent<HTMLElement>, cancelled?: boolean) => void;
};

// Apple's response/damping parameters, expressed as a unit-mass spring.
const RESPONSE = 0.3;
const FREQUENCY = 2 * Math.PI / RESPONSE;

export function useSheetMotion(dialog: RefObject<HTMLDialogElement | null>, open: boolean, onClose: () => void) {
  const [present, setPresent] = useState(open);
  const motion = useRef<SheetMotion | null>(null);
  const close = useRef(onClose);
  useLayoutEffect(() => { close.current = onClose; }, [onClose]);
  useEffect(() => { if (open) setPresent(true); }, [open]);

  useLayoutEffect(() => {
    const element = dialog.current;
    if (!present || !element) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    element.showModal();
    document.body.style.overflow = 'hidden';

    let closedPosition = element.getBoundingClientRect().height + 24;
    let position = reducedMotion.matches ? 0 : closedPosition;
    let velocity = 0;
    let target = 0;
    let damping = 1;
    let frame = 0;
    let lastFrame = 0;
    let complete: (() => void) | undefined;
    let pointer: { id: number; origin: number; startY: number; lastY: number; lastTime: number; velocity: number } | null = null;

    function paint() {
      element!.style.transform = `translate3d(0, ${position}px, 0)`;
      element!.style.setProperty('--sheet-backdrop-opacity', String(0.4 * (1 - Math.min(1, Math.max(0, position / closedPosition)))));
    }

    function stop() {
      cancelAnimationFrame(frame);
      frame = 0;
      complete = undefined;
    }

    function finish() {
      position = target;
      velocity = 0;
      frame = 0;
      paint();
      const callback = complete;
      complete = undefined;
      callback?.();
    }

    function tick(time: number) {
      // Substeps keep the spring stable at low frame rates and after a background tab resumes.
      let remaining = Math.min((time - lastFrame) / 1000, 0.032);
      lastFrame = time;
      while (remaining > 0) {
        const dt = Math.min(remaining, 1 / 120);
        velocity += (-(FREQUENCY ** 2) * (position - target) - 2 * damping * FREQUENCY * velocity) * dt;
        position += velocity * dt;
        if (position < 0) { position = 0; velocity = Math.max(0, velocity); }
        remaining -= dt;
      }
      paint();
      if (Math.abs(position - target) < 0.5 && Math.abs(velocity) < 5) finish();
      else frame = requestAnimationFrame(tick);
    }

    function animate(next: number, initialVelocity = velocity, done?: () => void) {
      stop();
      target = next;
      velocity = initialVelocity;
      damping = Math.abs(initialVelocity) > 5 ? 0.8 : 1;
      complete = done;
      if (reducedMotion.matches) { finish(); return; }
      lastFrame = performance.now();
      frame = requestAnimationFrame(tick);
    }

    function dismiss(notify = true) {
      animate(closedPosition, velocity, () => {
        if (notify) close.current();
        setPresent(false);
      });
    }

    motion.current = {
      settle: () => animate(0),
      dismiss,
      grab(event) {
        if (!event.isPrimary || event.button !== 0) return;
        stop();
        pointer = { id: event.pointerId, origin: position, startY: event.clientY, lastY: event.clientY, lastTime: event.timeStamp, velocity: 0 };
        event.currentTarget.setPointerCapture(event.pointerId);
      },
      drag(event) {
        if (!pointer || event.pointerId !== pointer.id) return;
        const elapsed = event.timeStamp - pointer.lastTime;
        if (elapsed > 0) pointer.velocity = (event.clientY - pointer.lastY) / elapsed * 1000;
        pointer.lastY = event.clientY;
        pointer.lastTime = event.timeStamp;
        const next = pointer.origin + event.clientY - pointer.startY;
        // Progressive resistance at the upper edge; preserve the exact grab offset.
        position = next < 0 ? next * closedPosition * 0.55 / (closedPosition + 0.55 * Math.abs(next)) : next;
        paint();
      },
      release(event, cancelled = false) {
        if (!pointer || event.pointerId !== pointer.id) return;
        velocity = event.timeStamp - pointer.lastTime > 100 ? 0 : pointer.velocity;
        pointer = null;
        if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
        // Exponential scroll projection makes a short flick count, and an upward reversal cancel.
        const projected = position + (velocity / 1000) * 0.998 / (1 - 0.998);
        if (!cancelled && projected > closedPosition / 2) dismiss();
        else animate(0, velocity);
      },
    };

    function preferenceChanged() { if (reducedMotion.matches && frame) { cancelAnimationFrame(frame); finish(); } }
    reducedMotion.addEventListener('change', preferenceChanged);
    const observer = new ResizeObserver(() => {
      closedPosition = element!.getBoundingClientRect().height + 24;
      if (target > 0) target = closedPosition;
      paint();
    });
    observer.observe(element);
    paint();

    return () => {
      stop();
      observer.disconnect();
      reducedMotion.removeEventListener('change', preferenceChanged);
      motion.current = null;
      element.close();
      document.body.style.overflow = previousOverflow;
      if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
    };
  }, [dialog, present]);

  useLayoutEffect(() => {
    if (open) motion.current?.settle();
    else motion.current?.dismiss(false);
  }, [open, present]);

  return {
    present,
    dismiss: () => motion.current?.dismiss(),
    onPointerDown: (event: PointerEvent<HTMLElement>) => { if (open) motion.current?.grab(event); },
    onPointerMove: (event: PointerEvent<HTMLElement>) => motion.current?.drag(event),
    onPointerUp: (event: PointerEvent<HTMLElement>) => motion.current?.release(event),
    onPointerCancel: (event: PointerEvent<HTMLElement>) => motion.current?.release(event, true),
    onLostPointerCapture: (event: PointerEvent<HTMLElement>) => motion.current?.release(event, true),
  };
}
