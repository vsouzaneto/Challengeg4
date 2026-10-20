import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { GroupKey, Headline } from "@/copy/pt-BR";

/** Nível 1 de um cartão de análise: número protagonista + frase curta e, só onde a API manda `share`, uma barra
 * (`aria-hidden`: o leitor de tela não ouve um "por cento" que a API não mandou). */
export function HeadlineMetrics({ headline, tone }: { headline: Headline; tone?: GroupKey }) {
  if (!headline.metrics.length && !headline.chips?.length) return null;
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-x-6 gap-y-2">
        {headline.metrics.map((metric) => (
          <div key={`${metric.value}-${metric.label}`} className="flex min-w-0 flex-1 basis-40 flex-col gap-1">
            <p className="flex flex-wrap items-baseline gap-x-1.5">
              <span className="text-2xl font-semibold tabular-nums">{metric.value}</span>
              <span className="text-sm text-muted-foreground">{metric.label}</span>
            </p>
            {metric.share !== undefined && (
              <Progress aria-hidden value={metric.share * 100} tone={tone ?? "neutral"} />
            )}
          </div>
        ))}
      </div>
      {headline.chips && headline.chips.length > 0 && (
        <ul className="flex flex-wrap gap-1.5">
          {headline.chips.map((chip) => (
            <li key={chip}><Badge variant="outline">{chip}</Badge></li>
          ))}
        </ul>
      )}
    </div>
  );
}
