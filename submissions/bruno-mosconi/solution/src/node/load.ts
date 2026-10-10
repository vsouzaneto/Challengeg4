// Lê os CSVs do disco (testes e scripts). No navegador, o app importa os mesmos arquivos com ?raw.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { type Dataset, parseDataset, type RawTables } from "../core/data.ts";

export const DATA_DIR = fileURLToPath(new URL("../../data/", import.meta.url));

export function readRaw(dir = DATA_DIR): RawTables {
	const read = (f: string) => readFileSync(`${dir}${f}`, "utf8");
	return {
		accounts: read("accounts.csv"),
		products: read("products.csv"),
		salesPipeline: read("sales_pipeline.csv"),
		salesTeams: read("sales_teams.csv"),
	};
}

export const loadDataset = (dir = DATA_DIR): Dataset =>
	parseDataset(readRaw(dir));
