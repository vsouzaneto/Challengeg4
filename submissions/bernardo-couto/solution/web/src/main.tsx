import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// `npm run dev:mock` (vite --mode mock) serves fixtures from a browser service worker.
// The MODE check is constant-folded in production builds, so the mocks never ship.
const MOCK = import.meta.env.MODE === 'mock';

async function bootstrap() {
  if (MOCK) {
    const { startBrowserMocks } = await import('./mocks/browser');
    await startBrowserMocks();
  }
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App mockBanner={MOCK} />
    </StrictMode>,
  );
}

void bootstrap();
