import type { ReactNode } from "react";
import Link from "next/link";

// Small renderer for the generated local proposal: no HTML execution or remote embeds.
function inline(text: string): ReactNode[] {
  return text
    .split(/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*[^*\n]+\*)/g)
    .map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**"))
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      if (part.startsWith("`") && part.endsWith("`"))
        return <code key={i}>{part.slice(1, -1)}</code>;
      if (part.startsWith("*") && part.endsWith("*"))
        return <em key={i}>{part.slice(1, -1)}</em>;
      const match = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (match) {
        const local: Record<string, string> = {
          "diagnostico.md": "/#cenario",
          "modelo.md": "/modelo",
          "automacao.md": "/proposta",
        };
        const href = local[match[2]];
        if (href)
          return (
            <Link key={i} href={href}>
              {match[1]}
            </Link>
          );
        if (/^https:\/\//i.test(match[2]))
          return (
            <a key={i} href={match[2]} target="_blank" rel="noreferrer">
              {match[1]}
            </a>
          );
        return <span key={i}>{match[1]}</span>;
      }
      return part;
    });
}
const cells = (line: string) =>
  line
    .trim()
    .replace(/^\||\|$/g, "")
    .split("|")
    .map((cell) => cell.trim());

export function Document({ text }: { text: string }) {
  const lines = text.replace(/<!--[\s\S]*?-->/g, "").split(/\r?\n/);
  const blocks: ReactNode[] = [];
  for (let index = 0; index < lines.length;) {
    const line = lines[index].trim();
    if (!line) {
      index++;
      continue;
    }
    const key = index;
    if (line.startsWith("```")) {
      const code: string[] = [];
      index++;
      while (index < lines.length && !lines[index].trim().startsWith("```"))
        code.push(lines[index++]);
      blocks.push(<pre key={key}>{code.join("\n")}</pre>);
      index++;
      continue;
    }
    if (
      line.startsWith("|") &&
      /^\s*\|[\s:|-]+\|\s*$/.test(lines[index + 1] ?? "")
    ) {
      const headings = cells(line);
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length && lines[index].trim().startsWith("|"))
        rows.push(cells(lines[index++]));
      blocks.push(
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label={`Tabela: ${headings.join(", ")}`}
          key={key}
        >
          <table>
            <thead>
              <tr>
                {headings.map((heading, i) => (
                  <th scope="col" key={i}>
                    {inline(heading)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{inline(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      blocks.push(
        heading[1].length <= 2 ? (
          <h2 key={key}>{inline(heading[2])}</h2>
        ) : heading[1].length === 3 ? (
          <h3 key={key}>{inline(heading[2])}</h3>
        ) : (
          <h4 key={key}>{inline(heading[2])}</h4>
        ),
      );
      index++;
      continue;
    }
    if (/^[-*]\s/.test(line) || /^\d+\.\s/.test(line)) {
      const ordered = /^\d+\.\s/.test(line);
      const items: ReactNode[] = [];
      const pattern = ordered ? /^\d+\.\s+/ : /^[-*]\s+/;
      while (index < lines.length && pattern.test(lines[index].trim())) {
        items.push(
          <li key={index}>
            {inline(lines[index].trim().replace(pattern, ""))}
          </li>,
        );
        index++;
      }
      blocks.push(
        ordered ? <ol key={key}>{items}</ol> : <ul key={key}>{items}</ul>,
      );
      continue;
    }
    if (line.startsWith(">")) {
      blocks.push(
        <blockquote key={key}>{inline(line.replace(/^>\s*/, ""))}</blockquote>,
      );
      index++;
      continue;
    }
    if (/^---+$/.test(line)) {
      blocks.push(<hr key={key} />);
      index++;
      continue;
    }
    const paragraph = [line];
    index++;
    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^(#|\||>|```|[-*]\s|\d+\.\s)/.test(lines[index].trim())
    )
      paragraph.push(lines[index++].trim());
    blocks.push(<p key={key}>{inline(paragraph.join(" "))}</p>);
  }
  return <article className="document">{blocks}</article>;
}
