import { notFound } from "next/navigation";
import { getTicketByToken } from "@/lib/tickets";
import { PortalChat } from "@/components/portal/PortalChat";

export const dynamic = "force-dynamic";

export default async function TicketChat({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const t = await getTicketByToken(token);
  if (!t) notFound();
  return <PortalChat token={token} />;
}
