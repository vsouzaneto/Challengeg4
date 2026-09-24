// Session-scoped record of actions the seller took (optimistic UI). The API log is
// append-only; "undo" only clears the local badge/discard (see t.actions.undoHint).
import { createContext, useContext } from 'react';
import type { FeedbackAction } from '../../api/client';

export type UiAction =
  'contacted' | 'meeting' | 'proposal' | 'discard' | 'accountFixed' | 'closedInCrm';
export const UI_TO_API: Record<UiAction, FeedbackAction> = {
  contacted: 'contacted',
  meeting: 'meeting_scheduled',
  proposal: 'proposal_sent',
  discard: 'discard',
  accountFixed: 'account_fixed',
  closedInCrm: 'closed_in_crm',
};

export interface DealFeedback {
  action: UiAction;
  status: 'pending' | 'ok' | 'error';
  recordedAt?: string; // ISO from the API (the only real clock, audit only)
  errorMessage?: string;
}

export interface FeedbackState {
  byDeal: Record<string, DealFeedback>;
  discarded: Record<string, true>;
}

export type FeedbackEvent =
  | { type: 'start'; id: string; action: UiAction }
  | { type: 'ok'; id: string; action: UiAction; recordedAt: string }
  | { type: 'error'; id: string; action: UiAction; message: string }
  | { type: 'undo'; id: string }
  | { type: 'clear-error'; id: string };

export function feedbackReducer(state: FeedbackState, ev: FeedbackEvent): FeedbackState {
  switch (ev.type) {
    case 'start': {
      const discarded = { ...state.discarded };
      if (ev.action === 'discard') discarded[ev.id] = true;
      return {
        byDeal: { ...state.byDeal, [ev.id]: { action: ev.action, status: 'pending' } },
        discarded,
      };
    }
    case 'ok':
      return {
        ...state,
        byDeal: {
          ...state.byDeal,
          [ev.id]: { action: ev.action, status: 'ok', recordedAt: ev.recordedAt },
        },
      };
    case 'error': {
      // Roll back the optimistic state; keep the error for the toast.
      const discarded = { ...state.discarded };
      delete discarded[ev.id];
      return {
        byDeal: {
          ...state.byDeal,
          [ev.id]: { action: ev.action, status: 'error', errorMessage: ev.message },
        },
        discarded,
      };
    }
    case 'undo':
    case 'clear-error': {
      const byDeal = { ...state.byDeal };
      delete byDeal[ev.id];
      const discarded = { ...state.discarded };
      delete discarded[ev.id];
      return { byDeal, discarded };
    }
  }
}

export const initialFeedbackState: FeedbackState = { byDeal: {}, discarded: {} };

export interface FeedbackApi {
  state: FeedbackState;
  record: (id: string, action: UiAction, actor: string) => void;
  undo: (id: string) => void;
  clearError: (id: string) => void;
}

export const FeedbackContext = createContext<FeedbackApi | null>(null);

export function useFeedback(): FeedbackApi {
  const ctx = useContext(FeedbackContext);
  if (!ctx) throw new Error('FeedbackContext missing');
  return ctx;
}
