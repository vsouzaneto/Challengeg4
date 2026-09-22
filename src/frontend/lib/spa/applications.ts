export type SpaApplication = {
  name: "@g4/chatbot" | "@g4/dashboards";
  title: string;
  activeWhen: "/sdk/chatbot" | "/sdk/dashboards";
  originEnv: "NEXT_PUBLIC_SPA_CHATBOT_ORIGIN" | "NEXT_PUBLIC_SPA_DASHBOARDS_ORIGIN";
  defaultOrigin: string;
  testId: string;
};

export const SPA_APPLICATIONS: readonly SpaApplication[] = [
  {
    name: "@g4/chatbot",
    title: "Chatbot",
    activeWhen: "/sdk/chatbot",
    originEnv: "NEXT_PUBLIC_SPA_CHATBOT_ORIGIN",
    defaultOrigin: "http://localhost:3030",
    testId: "spa-chatbot",
  },
  {
    name: "@g4/dashboards",
    title: "Dashboards",
    activeWhen: "/sdk/dashboards",
    originEnv: "NEXT_PUBLIC_SPA_DASHBOARDS_ORIGIN",
    defaultOrigin: "http://localhost:3010",
    testId: "spa-dashboards",
  },
] as const;

export function originOf(application: SpaApplication): string {
  const fromEnv = process.env[application.originEnv]?.trim();
  return (fromEnv || application.defaultOrigin).replace(/\/$/, "");
}

export function isSpaPath(pathname: string): boolean {
  return SPA_APPLICATIONS.some(
    (application) =>
      pathname === application.activeWhen ||
      pathname.startsWith(`${application.activeWhen}/`),
  );
}

export function childUrl(application: SpaApplication, pathname: string): string {
  const origin = originOf(application);
  const prefix = application.activeWhen;
  const rest = pathname.startsWith(prefix) ? pathname.slice(prefix.length) : "";
  const suffix = rest && rest !== "/" ? rest : "/";
  const url = new URL(`${origin}${suffix}`);
  url.searchParams.set("embed", "1");
  return url.toString();
}
