"use client";

import { CalendarX, CircleSlash, Database, Info, Scale, X, type LucideIcon } from "lucide-react";
import { type ReactNode, useState } from "react";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { INTELLIGENCE, UI, type Diagnostic, type Finding, type GroupKey } from "@/copy/pt-BR";
import type { IntelligenceFilter } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import type { DealOutcome, Dimension } from "@/lib/intelligence";

import { CrmGapsCard } from "./crm-gaps-card";
import { DiagnosticsList } from "./diagnostics-list";
import { FindingsList } from "./findings-list";

export type Panel = "analyses" | "guide";

/** Painel lateral da Inteligência: título, uma linha do que ele traz e o conteúdo com rolagem própria. A largura
 * usa a mesma variante do primitivo (data-[side=right]), senão a dele vence. */
function SidePanel({ open, onClose, title, description, children }: {
  open: boolean; onClose: () => void; title: string; description: string; children: ReactNode;
}) {
  return (
    <Sheet open={open} onOpenChange={(next) => !next && onClose()}>
      <SheetContent side="right" showCloseButton={false}
                    className="gap-0 data-[side=right]:w-full data-[side=right]:sm:max-w-2xl">
        <SheetHeader className="border-b">
          <div className="flex items-start justify-between gap-2">
            <div className="flex flex-col gap-1.5">
              <SheetTitle className="text-lg font-semibold">{title}</SheetTitle>
              <SheetDescription>{description}</SheetDescription>
            </div>
            <SheetClose asChild>
              <Button variant="ghost" size="icon-sm" aria-label={UI.closePanel}>
                <X aria-hidden />
              </Button>
            </SheetClose>
          </div>
        </SheetHeader>
        <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">{children}</div>
      </SheetContent>
    </Sheet>
  );
}

type AnalysesProps = {
  open: boolean;
  onClose: () => void;
  diagnostics: Diagnostic[];
  findings: Finding[];
  filter: IntelligenceFilter;
  onDeals: (outcome: DealOutcome, group?: GroupKey) => void;
  onViewBy: (dimension: Dimension) => void;
  onJump: (section: string) => void;
};

/** "Ver análises": os diagnósticos do processo e as descobertas do recorte, em duas abas. */
export function AnalysesPanel({ open, onClose, diagnostics, findings, filter, onDeals, onViewBy, onJump }: AnalysesProps) {
  const text = INTELLIGENCE.analyses;
  const [tab, setTab] = useState("processo");
  const count = (n: number) => <Badge variant="secondary" className="tabular-nums">{formatInt(n)}</Badge>;
  return (
    <SidePanel open={open} onClose={onClose} title={text.title} description={text.help}>
      <CrmGapsCard />
      <Tabs value={tab} onValueChange={setTab} className="gap-4">
        <TabsList aria-label={text.tabsLabel}>
          <TabsTrigger value="processo">{text.process}{count(diagnostics.length)}</TabsTrigger>
          <TabsTrigger value="resultados">{text.findings}{count(findings.length)}</TabsTrigger>
        </TabsList>
        <TabsContent value="processo">
          <DiagnosticsList diagnostics={diagnostics} filter={filter} onDeals={onDeals} onViewBy={onViewBy}
                           onJump={onJump} />
        </TabsContent>
        <TabsContent value="resultados">
          <FindingsList findings={findings} onViewBy={onViewBy} onJump={onJump} />
        </TabsContent>
      </Tabs>
    </SidePanel>
  );
}

const LIMIT_ICONS: LucideIcon[] = [CircleSlash, Scale, CalendarX, Database];

/** "Como funciona": cada definição numa entrada do accordion (o texto fica no DOM, fechado), como explorar e o que a
 * página não faz, com ícone. */
export function GuidePanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { guide, reading } = INTELLIGENCE;
  const entries = [
    ...reading.definitions.map((line, index) => ({ title: reading.definitionTitles[index] ?? line, line })),
    { title: reading.exploreTitle, line: guide.explore },
  ];
  return (
    <SidePanel open={open} onClose={onClose} title={guide.title} description={guide.help}>
      <section className="flex flex-col gap-1">
        <h3 className="text-sm font-semibold">{reading.title}</h3>
        <Accordion type="multiple">
          {entries.map((entry) => (
            <AccordionItem key={entry.title} value={entry.title}>
              <AccordionTrigger>{entry.title}</AccordionTrigger>
              <AccordionContent forceMount className="text-muted-foreground">{entry.line}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>
      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-semibold">{reading.limitsTitle}</h3>
        <ul className="flex flex-col gap-2 text-sm text-muted-foreground">
          {reading.limits.map((line, index) => {
            const Icon = LIMIT_ICONS[index] ?? Info;
            return (
              <li key={line} className="flex items-start gap-2">
                <Icon aria-hidden className="mt-0.5 size-4 shrink-0" />
                <span>{line}</span>
              </li>
            );
          })}
        </ul>
      </section>
    </SidePanel>
  );
}
