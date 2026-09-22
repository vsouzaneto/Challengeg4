import { registerApplication, start } from "single-spa";
import { isSpaPath, SPA_APPLICATIONS } from "./applications";
import { createIframeApplication } from "./iframe-application";

let started = false;

export function startRootConfig(): void {
  if (typeof window === "undefined" || !isSpaPath(window.location.pathname)) {
    return;
  }

  if (!started) {
    for (const application of SPA_APPLICATIONS) {
      registerApplication({
        name: application.name,
        app: () => Promise.resolve(createIframeApplication(application)),
        activeWhen: (location) =>
          location.pathname === application.activeWhen ||
          location.pathname.startsWith(`${application.activeWhen}/`),
      });
    }
    start({ urlRerouteOnly: true });
    started = true;
  }
}
