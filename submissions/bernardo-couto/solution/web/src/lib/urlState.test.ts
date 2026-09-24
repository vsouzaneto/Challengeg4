import { applyPatch, readState, writeState } from './urlState';

describe('urlState', () => {
  const base = readState(
    new URLSearchParams(
      'as_of=2017-12-31&region=Central&manager=M&agent=A&n=25&sort=days&offset=25&deal=X',
    ),
  );

  it('round-trips through the URL', () => {
    expect(writeState(base).toString()).toBe(
      'as_of=2017-12-31&region=Central&manager=M&agent=A&n=25&sort=days&offset=25&deal=X',
    );
    expect(writeState(readState(new URLSearchParams(''))).toString()).toBe('');
  });

  it('clears the hierarchy below the changed level and resets paging', () => {
    expect(applyPatch(base, { region: 'East' })).toMatchObject({
      region: 'East',
      manager: undefined,
      agent: undefined,
      offset: 0,
    });
    expect(applyPatch(base, { manager: 'N' })).toMatchObject({
      region: 'Central',
      manager: 'N',
      agent: undefined,
      offset: 0,
    });
    expect(applyPatch(base, { agent: 'B' })).toMatchObject({ manager: 'M', agent: 'B', offset: 0 });
    expect(applyPatch(base, { deal: undefined }).offset).toBe(25);
  });

  it('falls back to defaults on garbage', () => {
    expect(readState(new URLSearchParams('n=abc&sort=zzz&offset=-3'))).toMatchObject({
      n: 10,
      sort: 'score',
      offset: 0,
    });
  });
});
