import { expect, test } from '../fixtures';

test.describe('/api/genie', () => {
  test('should list the four lab rooms when GET /rooms is called', async ({
    adaContext,
  }) => {
    const response = await adaContext.request.get('/api/genie/rooms');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.rooms).toHaveLength(4);
    expect(data.rooms.map((room: { alias: string }) => room.alias)).toEqual([
      'churn',
      'support',
      'crm',
      'social',
    ]);
  });

  test('should reject an empty message when POST messages is called', async ({
    adaContext,
  }) => {
    const response = await adaContext.request.post('/api/genie/churn/messages', {
      data: { content: '   ' },
    });
    expect([400, 503]).toContain(response.status());
  });

  test('should return not found when the room alias is unknown', async ({
    adaContext,
  }) => {
    const response = await adaContext.request.post(
      '/api/genie/unknown/messages',
      { data: { content: 'quantas contas?' } },
    );
    expect(response.status()).toBe(404);
  });
});
