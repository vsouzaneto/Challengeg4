import { useCallback, useMemo, useReducer, type ReactNode } from 'react';
import { api, ApiError } from '../../api/client';
import { useToast } from '../../components/Toast';
import { t } from '../../i18n/pt-BR';
import {
  FeedbackContext,
  feedbackReducer,
  initialFeedbackState,
  UI_TO_API,
  type UiAction,
} from './feedbackStore';

/** Optimistic feedback: badge first, POST after; error rolls back and toasts a retry. */
export function FeedbackProvider({ asOf, children }: { asOf?: string; children: ReactNode }) {
  const [state, dispatch] = useReducer(feedbackReducer, initialFeedbackState);
  const toast = useToast();

  const undo = useCallback((id: string) => dispatch({ type: 'undo', id }), []);
  const clearError = useCallback((id: string) => dispatch({ type: 'clear-error', id }), []);

  const record = useCallback(
    (id: string, action: UiAction, actor: string) => {
      dispatch({ type: 'start', id, action });
      if (action === 'discard') {
        toast.push({
          kind: 'status',
          message: t.actions.discarded(1),
          actionLabel: t.actions.undo,
          onAction: () => undo(id),
          durationMs: 8000,
        });
      }
      api
        .createFeedback({ opportunity_id: id, action: UI_TO_API[action], actor }, asOf)
        .then((rec) => dispatch({ type: 'ok', id, action, recordedAt: rec.recorded_at }))
        .catch((err: unknown) => {
          const message = err instanceof ApiError ? err.message : String(err);
          dispatch({ type: 'error', id, action, message });
          toast.push({
            kind: 'alert',
            message: t.actions.error,
            actionLabel: t.actions.retry,
            onAction: () => record(id, action, actor),
          });
        });
    },
    [asOf, toast, undo],
  );

  const value = useMemo(
    () => ({ state, record, undo, clearError }),
    [state, record, undo, clearError],
  );
  return <FeedbackContext.Provider value={value}>{children}</FeedbackContext.Provider>;
}
