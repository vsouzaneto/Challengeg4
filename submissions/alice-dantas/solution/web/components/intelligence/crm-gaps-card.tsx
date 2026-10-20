"use client";

import {
  Building2, ClipboardList, HelpCircle, MessagesSquare, PhoneCall, type LucideIcon,
} from "lucide-react";

import { IconTile } from "@/components/app/icon-tile";
import { MoreDetails } from "@/components/app/more-details";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { INTELLIGENCE } from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";

const text = INTELLIGENCE.process;

/** Um ícone por lacuna, na mesma ordem de `crmGapsShort`. */
const CRM_ICONS: LucideIcon[] = [
  PhoneCall, MessagesSquare, ClipboardList, CONCEPT_ICONS.order, Building2, HelpCircle, CONCEPT_ICONS.listPrice,
];

/** O que o CRM não registra. Abre o painel "Ver análises" para deixar claro que nenhuma das análises abaixo considera
 * estes pontos. A lista curta fica à vista e o que cada um quer dizer, no detalhe. */
export function CrmGapsCard() {
  return (
    <Card size="sm" className="shrink-0">
      <CardHeader>
        <CardTitle className="font-semibold">{text.crmTitle}</CardTitle>
        <p className="text-sm text-muted-foreground">{text.crmHelp}</p>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <ul className="flex flex-col gap-2 text-sm">
          {text.crmGapsShort.map((gap, index) => {
            const Icon = CRM_ICONS[index] ?? CONCEPT_ICONS.info;
            return (
              <li key={gap} className="flex items-center gap-2">
                <IconTile icon={Icon} size="sm" />
                {gap}
              </li>
            );
          })}
        </ul>
        <MoreDetails label={text.detail} contentClassName="flex flex-col gap-1.5 text-sm text-muted-foreground">
          <ul className="flex list-disc flex-col gap-1.5 pl-4">
            {text.crmGaps.map((gap) => <li key={gap}>{gap}</li>)}
          </ul>
        </MoreDetails>
      </CardContent>
    </Card>
  );
}
