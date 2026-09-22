import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SDK Dashboards",
  description:
    "Single-SPA monta o monorepo aibi-dashboards-external-embedding em localhost:3010.",
};

export default function SdkDashboardsPage() {
  return <h1 className="sr-only">SDK Dashboards</h1>;
}
