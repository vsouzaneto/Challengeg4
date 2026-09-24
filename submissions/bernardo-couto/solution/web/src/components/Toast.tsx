import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { t } from '../i18n/pt-BR';

export interface Toast {
  id: number;
  kind: 'status' | 'alert';
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  durationMs?: number;
}

interface ToastApi {
  push: (toast: Omit<Toast, 'id'>) => number;
  dismiss: (id: number) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('ToastContext missing');
  return ctx;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());
  const seq = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((ts) => ts.filter((x) => x.id !== id));
    const timer = timers.current.get(id);
    if (timer) clearTimeout(timer);
    timers.current.delete(id);
  }, []);

  const schedule = useCallback(
    (toast: Toast) => {
      const timer = setTimeout(() => dismiss(toast.id), toast.durationMs ?? 8000);
      timers.current.set(toast.id, timer);
    },
    [dismiss],
  );

  const push = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const full: Toast = { ...toast, id: ++seq.current };
      setToasts((ts) => [...ts, full]);
      schedule(full);
      return full.id;
    },
    [schedule],
  );

  const pause = (id: number) => {
    const timer = timers.current.get(id);
    if (timer) clearTimeout(timer);
  };
  const resume = (toast: Toast) => schedule(toast);

  const api = useMemo(() => ({ push, dismiss }), [push, dismiss]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role={toast.kind}
            className={`pointer-events-auto flex items-center gap-3 rounded px-4 py-3 text-sm text-white shadow-xl ${
              toast.kind === 'alert' ? 'bg-g4-risk' : 'bg-g4-primary'
            }`}
            onMouseEnter={() => pause(toast.id)}
            onMouseLeave={() => resume(toast)}
            onFocus={() => pause(toast.id)}
            onBlur={() => resume(toast)}
          >
            <span>{toast.message}</span>
            {toast.actionLabel && toast.onAction && (
              <button
                type="button"
                className="rounded underline decoration-2 underline-offset-2 font-semibold"
                onClick={() => {
                  toast.onAction?.();
                  dismiss(toast.id);
                }}
              >
                {toast.actionLabel}
              </button>
            )}
            <button
              type="button"
              className="ml-1 rounded px-1 text-base leading-none"
              aria-label={t.actions.closeToast}
              onClick={() => dismiss(toast.id)}
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
