"use client";

import { ChartColumn, MoveDown } from "lucide-react";

import { MoreDetails } from "@/components/app/more-details";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
  INTELLIGENCE, PEOPLE_DIMENSIONS, PEOPLE_DRIVERS_NOTE, findingHeadline, findingText, type Finding,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import type { Dimension } from "@/lib/intelligence";

import { DriverBar } from "./driver-bar";
import { HeadlineMetrics } from "./headline-metrics";

const text = INTELLIGENCE.findings;
const KIND_ICONS = { descriptive: ChartColumn, statistical: CONCEPT_ICONS.compare } as const;

/** O recorte em que cada descoberta pode ser conferida, quando há um. */
function findingDimension(finding: Finding): Dimension | null {
  switch (finding.code) {
    case "win_rate_beyond_chance":
    case "revenue_concentrated":
    case "revenue_gap_drivers":
      return finding.params.dimension;
    case "account_product_coverage":
      return "account";
    default:
      return null;
  }
}

/** O que os resultados mostram: número protagonista e, na decomposição, a barra de três fatores; o texto inteiro
 * fica em "Ver detalhe". Fica no painel "Ver análises"; o botão leva ao recorte em que a descoberta pode ser conferida. */
export function FindingsList({ findings, onViewBy, onJump }: {
  findings: Finding[]; onViewBy: (d: Dimension) => void; onJump: (section: string) => void;
}) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">{text.help}</p>
      {findings.length === 0 && <p className="text-sm text-muted-foreground">{text.none}</p>}
      {findings.map((finding, index) => {
        const { title, body, kind } = findingText(finding);
        const dimension = findingDimension(finding);
        const KindIcon = KIND_ICONS[kind];
        const people = finding.code === "revenue_gap_drivers" && PEOPLE_DIMENSIONS.includes(finding.params.dimension);
        return (
          <Card key={`${finding.code}-${index}`} size="sm">
            <CardHeader>
              <Badge variant={kind === "statistical" ? "secondary" : "outline"}>
                <KindIcon data-icon="inline-start" aria-hidden />
                {text.kinds[kind]}
              </Badge>
              <CardTitle className="font-semibold text-pretty">{title}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <HeadlineMetrics headline={findingHeadline(finding)} />
              {finding.code === "revenue_gap_drivers" && <DriverBar drivers={finding.params.drivers} />}
              {people && <p className="text-xs text-muted-foreground">{PEOPLE_DRIVERS_NOTE}</p>}
              <MoreDetails label={INTELLIGENCE.process.detail}>
                <p className="text-sm text-pretty text-muted-foreground">{body}</p>
              </MoreDetails>
            </CardContent>
            {(dimension || finding.code === "fast_losses") && (
              <CardFooter>
                {dimension ? (
                  <Button variant="outline" size="sm" onClick={() => onViewBy(dimension)}>{text.seeBy(dimension)}</Button>
                ) : (
                  <Button variant="outline" size="sm" onClick={() => onJump("tempo")}>
                    <MoveDown aria-hidden />
                    {INTELLIGENCE.process.seeMonths}
                  </Button>
                )}
              </CardFooter>
            )}
          </Card>
        );
      })}
    </div>
  );
}
