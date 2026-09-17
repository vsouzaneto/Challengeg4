export type Data = Record<string, any>;
export type Context = { route: string; params: URLSearchParams; catalog: Data; signal: AbortSignal };
export type Mount = (root: HTMLElement, context: Context) => Promise<void | (() => void)>;
