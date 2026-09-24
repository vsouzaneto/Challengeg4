// Browser worker for `npm run dev:mock`. Scenario can be forced with `?mock=missing|error|empty`.
import { setupWorker } from 'msw/browser';
import { buildHandlers, type Scenario } from './handlers';

function scenarioFromUrl(): Scenario {
  const v = new URLSearchParams(window.location.search).get('mock');
  return v === 'missing' || v === 'error' || v === 'empty' ? v : 'ok';
}

export async function startBrowserMocks() {
  const worker = setupWorker(...buildHandlers(scenarioFromUrl));
  await worker.start({ onUnhandledRequest: 'bypass', quiet: true });
}
