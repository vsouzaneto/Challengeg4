type IconName = 'arrow' | 'check' | 'clock' | 'copy' | 'target' | 'chevron' | 'undo' | 'info';
const paths: Record<IconName, string> = {
  arrow: 'M5 12h14m-6-6 6 6-6 6', check: 'm5 12 4 4L19 6', clock: 'M12 8v4l3 2',
  copy: 'M9 9h10v11H9zM5 15H4V4h10v1', target: 'M12 3a9 9 0 1 0 9 9M12 7a5 5 0 1 0 5 5m-5 0 9-9m-6 0h6v6',
  chevron: 'm9 5 7 7-7 7', undo: 'M8 4 3 9l5 5M3 9h11a6 6 0 0 1 0 12', info: 'M12 11v6m0-10v1',
};
export function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{(name === 'clock' || name === 'info') && <circle cx="12" cy="12" r="9" />}<path d={paths[name]} /></svg>;
}
