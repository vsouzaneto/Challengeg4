import type { LifeCycles } from "single-spa";
import type { SpaApplication } from "./applications";
import { childUrl } from "./applications";

export function createIframeApplication(
  application: SpaApplication,
): LifeCycles {
  let frame: HTMLIFrameElement | null = null;

  function slot(): HTMLElement | null {
    return document.getElementById("single-spa-slot");
  }

  return {
    async bootstrap() {
      return undefined;
    },
    async mount() {
      const host = slot();
      if (!host) {
        return;
      }
      frame = document.createElement("iframe");
      frame.src = childUrl(application, window.location.pathname);
      frame.title = application.title;
      frame.setAttribute("data-testid", application.testId);
      frame.setAttribute("data-spa-name", application.name);
      frame.className = "h-full w-full border-0 bg-background";
      frame.referrerPolicy = "strict-origin-when-cross-origin";
      host.replaceChildren(frame);
    },
    async unmount() {
      const host = slot();
      if (host) {
        host.replaceChildren();
      }
      frame = null;
    },
  };
}
