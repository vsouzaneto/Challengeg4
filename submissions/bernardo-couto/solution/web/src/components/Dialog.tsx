import { useEffect, useRef, type ReactNode } from 'react';

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

interface Props {
  labelledBy: string;
  describedBy?: string;
  onClose: () => void;
  /** Element to focus on open; defaults to the first focusable. */
  initialFocus?: () => HTMLElement | null;
  /** Element to return focus to on close. */
  returnFocus?: () => HTMLElement | null;
  className?: string;
  children: ReactNode;
  side?: 'right' | 'left';
}

/**
 * Modal panel with focus trap, Esc to close, scrim click to close, body scroll lock and
 * focus return (accessibility.md §4). Used by the deal drawer and the mobile filter panel.
 */
export function Dialog({
  labelledBy,
  describedBy,
  onClose,
  initialFocus,
  returnFocus,
  className = '',
  children,
  side = 'right',
}: Props) {
  const panel = useRef<HTMLDivElement>(null);
  const returnRef = useRef(returnFocus);
  returnRef.current = returnFocus;

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const root = document.getElementById('root');
    root?.setAttribute('aria-hidden', 'true');
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const target = initialFocus?.() ?? panel.current?.querySelector<HTMLElement>(FOCUSABLE);
    target?.focus();

    return () => {
      root?.removeAttribute('aria-hidden');
      document.body.style.overflow = prevOverflow;
      const back = returnRef.current?.() ?? previouslyFocused;
      back?.focus?.();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const onDocKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onDocKey);
    return () => document.removeEventListener('keydown', onDocKey);
  }, [onClose]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') return; // handled at document level
    if (e.key !== 'Tab' || !panel.current) return;
    const items = Array.from(panel.current.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
      (el) => el.offsetParent !== null || el === document.activeElement,
    );
    if (items.length === 0) return;
    const first = items[0]!;
    const last = items[items.length - 1]!;
    const active = document.activeElement;
    if (e.shiftKey && (active === first || !panel.current.contains(active))) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex" onKeyDown={onKeyDown}>
      <div
        data-testid="scrim"
        className="absolute inset-0 bg-g4-primary/40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        aria-describedby={describedBy}
        className={`relative flex h-full max-w-full flex-col overflow-y-auto bg-white shadow-xl transition-transform duration-150 ease-out ${
          side === 'right' ? 'ml-auto' : 'mr-auto'
        } ${className}`}
      >
        {children}
      </div>
    </div>
  );
}
