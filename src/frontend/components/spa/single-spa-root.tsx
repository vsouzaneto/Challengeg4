"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { startRootConfig } from "@/lib/spa/root-config";

export function SingleSpaRoot() {
  const pathname = usePathname();

  useEffect(() => {
    startRootConfig();
  }, [pathname]);

  return (
    <div
      id="single-spa-slot"
      className="min-h-0 flex-1 pt-20"
      data-testid="single-spa-slot"
    />
  );
}
