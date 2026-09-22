import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { AppSidebar } from '@/components/app-sidebar';
import { SiteFooter } from '@/components/brand/site-footer';
import { SiteHeader } from '@/components/brand/site-header';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useSession } from '@/contexts/SessionContext';
import { DbIcon } from '@/components/ui/db-icon';
import { UserKeyIconIcon } from '@/components/icons';
import { isEmbeddedInHost } from '@/lib/embed';

function useEmbeddedInHost() {
  const [embedded, setEmbedded] = useState(() =>
    typeof window !== 'undefined' && isEmbeddedInHost(),
  );

  useEffect(() => {
    setEmbedded(isEmbeddedInHost());
  }, []);

  return embedded;
}

export default function ChatLayout() {
  const { session, loading } = useSession();
  const embedded = useEmbeddedInHost();
  const isCollapsed = localStorage.getItem('sidebar:state') !== 'true';
  const header = embedded ? null : <SiteHeader />;
  const topPad = embedded ? '' : 'pt-20';
  const shellHeight = embedded
    ? 'h-svh min-h-0'
    : 'mt-20 h-[calc(100svh-5rem)] min-h-0';

  // Wait for session to load
  if (loading) {
    return (
      <div className="g4-page flex min-h-svh flex-col">
        {header}
        <div className={`flex flex-1 items-center justify-center ${topPad}`}>
          <div className="text-muted-foreground">Carregando...</div>
        </div>
        <SiteFooter />
      </div>
    );
  }

  // No guest mode - redirect if no session
  if (!session?.user) {
    return (
      <div className="g4-page flex min-h-svh flex-col">
        {header}
        <div className={`flex flex-1 items-center justify-center bg-secondary ${topPad}`}>
          <div className="flex flex-col items-center gap-6">
            <img
              src="/brand/logo-g4-completa-branca.svg"
              alt="G4"
              className="h-8 w-auto g4s-logo-on-light"
            />
            <div className="flex w-80 flex-col items-center gap-4 rounded-[24px] border border-border bg-background p-10 shadow-[var(--g4s-shadow-card)]">
              <DbIcon icon={UserKeyIconIcon} size={32} color="muted" />
              <div className="flex flex-col items-center gap-1.5 text-center">
                <h3>Autenticação necessária</h3>
                <p className="text-muted-foreground">
                  Autentique-se com o Databricks para acessar este aplicativo.
                </p>
              </div>
            </div>
          </div>
        </div>
        <SiteFooter />
      </div>
    );
  }

  // Get preferred username from session (if available from headers)
  const preferredUsername = session.user.preferredUsername ?? null;

  return (
    <div className="g4-page flex min-h-svh flex-col">
      {header}
      <SidebarProvider
        defaultOpen={!isCollapsed}
        className={shellHeight}
      >
        <AppSidebar user={session.user} preferredUsername={preferredUsername} />
        <SidebarInset className="h-full overflow-hidden bg-secondary">
          <div className="flex flex-1 flex-col overflow-hidden bg-background shadow-[var(--g4s-shadow-card)] md:my-2 md:mr-2 md:rounded-[24px]">
            <Outlet />
          </div>
        </SidebarInset>
      </SidebarProvider>
      <SiteFooter />
    </div>
  );
}
