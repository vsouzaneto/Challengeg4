// Páginas do menu central: fonte única. Uma página nova é uma rota em app/ e uma linha aqui.
export const NAV_ITEMS = [
  { key: "carteira", href: "/carteira" },
  { key: "equipe", href: "/equipe" },
  { key: "inteligencia", href: "/inteligencia" },
  { key: "evidencia", href: "/evidencia" },
  { key: "comoFunciona", href: "/como-funciona" },
] as const;

export type NavKey = (typeof NAV_ITEMS)[number]["key"];

export const isActive = (pathname: string, href: string): boolean =>
  pathname === href || pathname.startsWith(`${href}/`);
