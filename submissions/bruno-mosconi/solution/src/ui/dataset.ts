// Os CSVs entram no bundle e passam pelo mesmo parser dos testes: sem chamada de rede (CA9).

import accounts from "../../data/accounts.csv?raw";
import products from "../../data/products.csv?raw";
import salesPipeline from "../../data/sales_pipeline.csv?raw";
import salesTeams from "../../data/sales_teams.csv?raw";
import { parseDataset } from "../core/data.ts";

export const dataset = parseDataset({
	accounts,
	products,
	salesPipeline,
	salesTeams,
});
