import { Brand } from "./brand";
import { DataBadge } from "./data-badge";
import { MainNav } from "./main-nav";
import { MobileNav } from "./mobile-nav";
import { ThemeToggle } from "./theme-toggle";

/** Cabeçalho único: marca, menu central (sem sidebar), data dos dados e tema. Abaixo de `lg` o menu vira um botão
 * ao lado do tema (as cinco páginas, a data e o tema não cabem numa linha antes disso), e o cabeçalho fica numa linha só. */
export function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-3 sm:px-6 lg:grid lg:h-16 lg:grid-cols-[1fr_auto_1fr] lg:py-0">
        <Brand />
        <MainNav className="hidden lg:flex lg:justify-self-center" />
        <div className="flex items-center justify-end gap-2 lg:justify-self-end">
          <DataBadge />
          <ThemeToggle />
          <MobileNav className="lg:hidden" />
        </div>
      </div>
    </header>
  );
}
