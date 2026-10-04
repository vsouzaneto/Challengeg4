import { PageHeader } from "@/components/ui";
import { CustomerEmulator } from "@/components/portal/CustomerEmulator";

export default function SimuladorPage() {
  return (
    <>
      <PageHeader kicker="Emulador" title="Simulador do cliente">
        Abra tickets como se fosse um cliente no site de suporte. Tudo passa pelo pipeline real e aparece na Smart Inbox (visão “Ao vivo”).
      </PageHeader>
      <div className="p-8"><CustomerEmulator /></div>
    </>
  );
}
