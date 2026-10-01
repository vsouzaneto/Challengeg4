import { fileURLToPath } from 'node:url';

/** Resolver pelo arquivo permite transportar solution/ para a submissão oficial. */
export const rawDirectory = fileURLToPath(new URL('../data/raw/', import.meta.url));
export const generatedDirectory = fileURLToPath(new URL('../data/generated/', import.meta.url));
