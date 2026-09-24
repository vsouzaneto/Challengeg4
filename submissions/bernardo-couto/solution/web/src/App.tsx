import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useMeta } from './api/queries';
import { Layout } from './components/Layout';
import { ToastProvider } from './components/Toast';
import { FeedbackProvider } from './features/feedback/FeedbackProvider';
import { useUrlState } from './lib/urlState';
import { QualityPage } from './pages/QualityPage';
import { QueuePage } from './pages/QueuePage';
import { TeamPage } from './pages/TeamPage';

export const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, refetchOnWindowFocus: false } },
});

/** Writes `default_as_of` into the URL when missing so shared links are dated (ux-spec §2). */
function AsOfSync({ children }: { children: React.ReactNode }) {
  const { state, update } = useUrlState();
  const meta = useMeta();
  useEffect(() => {
    if (!state.asOf && meta.data?.default_as_of) {
      update({ asOf: meta.data.default_as_of }, { replace: true });
    }
  }, [state.asOf, meta.data?.default_as_of, update]);
  return (
    <FeedbackProvider asOf={state.asOf ?? meta.data?.default_as_of ?? undefined}>
      {children}
    </FeedbackProvider>
  );
}

export function AppRoutes({ mockBanner }: { mockBanner?: boolean }) {
  return (
    <ToastProvider>
      <AsOfSync>
        <Routes>
          <Route element={<Layout mockBanner={mockBanner} />}>
            <Route index element={<QueuePage />} />
            <Route path="/time" element={<TeamPage />} />
            <Route path="/qualidade" element={<QualityPage />} />
          </Route>
        </Routes>
      </AsOfSync>
    </ToastProvider>
  );
}

export default function App({ mockBanner }: { mockBanner?: boolean }) {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes mockBanner={mockBanner} />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
