import { PageHeader } from "@/components/ui";
import { AskData } from "@/components/sql/AskData";
import { SUGGESTED_QUESTIONS } from "@/lib/sql/library";
import { llmEnabled } from "@/lib/ai/llm";

export default function PerguntasPage() {
  return (
    <>
      <PageHeader kicker="Text-to-SQL" title="Pergunte aos dados">
        Faça perguntas sobre a operação em português e veja o SQL, a tabela e o gráfico. O SQL é editável e sempre somente leitura.
      </PageHeader>
      <div className="p-8"><AskData suggestions={SUGGESTED_QUESTIONS} llm={llmEnabled()} /></div>
    </>
  );
}
