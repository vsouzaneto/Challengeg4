"use client";

import { useRouter } from "next/navigation";

interface Option {
  slug: string;
  name: string;
}

export function AgentSelect({ options, value, basePath }: { options: Option[]; value: string; basePath: string }) {
  const router = useRouter();
  return (
    <select
      aria-label="Selecionar"
      className="rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
      value={value}
      onChange={(e) => router.push(`${basePath}/${e.target.value}`)}
    >
      {options.map((o) => (
        <option key={o.slug} value={o.slug}>
          {o.name}
        </option>
      ))}
    </select>
  );
}
