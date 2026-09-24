import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

function parseLine(line: string): string[] {
  const fields: string[] = [];
  let value = "";
  let quoted = false;

  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];

    if (character === '"') {
      if (quoted && line[index + 1] === '"') {
        value += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === "," && !quoted) {
      fields.push(value);
      value = "";
    } else {
      value += character;
    }
  }

  if (quoted) {
    throw new Error("CSV contains an unterminated quoted field");
  }

  fields.push(value);
  return fields;
}

export type CsvRow = Record<string, string>;

export async function readCsv(fileName: string): Promise<CsvRow[]> {
  const content = await readFile(resolve(fileName), "utf8");
  const lines = content.split(/\r?\n/u).filter((line) => line.trim().length > 0);
  const headerLine = lines[0];
  if (!headerLine) {
    throw new Error(`CSV file is empty: ${fileName}`);
  }
  const headers = parseLine(headerLine);
  const rows: CsvRow[] = [];

  for (let index = 1; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line) {
      continue;
    }
    const values = parseLine(line);
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${index + 1} has ${values.length} fields; expected ${headers.length}`);
    }

    rows.push(Object.fromEntries(headers.map((header, headerIndex) => [header, values[headerIndex]?.trim() ?? ""])));
  }

  return rows;
}

export function required(row: CsvRow, key: string, fileName: string): string {
  const value = row[key]?.trim();
  if (!value) {
    throw new Error(`Missing ${key} in ${fileName}`);
  }
  return value;
}

export function optional(row: CsvRow, key: string): string | null {
  const value = row[key]?.trim();
  return value ? value : null;
}

export function numberValue(value: string | null): number | null {
  if (value === null || value === "") {
    return null;
  }

  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }
  return parsed;
}
