import { Badge } from "@/components/ui/badge";
import { GROUP_LABELS, type GroupKey } from "@/copy/pt-BR";
import { GROUP_VISUAL } from "@/copy/visual";

/** O badge do grupo com o ícone do grupo; o nome sempre acompanha a cor. */
export function GroupBadge({ state, className }: { state: GroupKey; className?: string }) {
  const Icon = GROUP_VISUAL[state].icon;
  return (
    <Badge variant={state} className={className}>
      <Icon data-icon="inline-start" aria-hidden />
      {GROUP_LABELS[state]}
    </Badge>
  );
}
