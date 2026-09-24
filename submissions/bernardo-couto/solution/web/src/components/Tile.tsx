import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface Props {
  value: ReactNode;
  label: string;
  hint?: string;
  to?: string;
  linkLabel?: string;
}

/** Stat tile: label above, 32px number, sub-label. Whole tile is a link when `to` is given. */
export function Tile({ value, label, hint, to, linkLabel }: Props) {
  const body = (
    <>
      <span className="block text-3xl font-bold tabular-nums">{value}</span>
      <span className="mt-1 block text-sm font-medium">{label}</span>
      {hint && <span className="mt-1 block text-xs font-medium text-g4-muted">{hint}</span>}
      {to && linkLabel && (
        <span className="mt-2 block text-xs font-semibold text-g4-navy700 underline">
          {linkLabel}
        </span>
      )}
    </>
  );
  if (to) {
    return (
      <Link to={to} className="card block p-4 hover:bg-g4-rowHover">
        {body}
      </Link>
    );
  }
  return <div className="card p-4">{body}</div>;
}
