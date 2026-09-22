import { expect, test } from '@playwright/test';
import {
  getLabRoom,
  isLabRoomAlias,
  LAB_ROOMS,
  listConfiguredLabRooms,
} from '@chat-template/core';

test.describe('LAB_ROOMS', () => {
  test('should expose four fixed rooms when catalog is loaded', () => {
    expect(LAB_ROOMS).toHaveLength(4);
    expect(LAB_ROOMS.map((room) => room.alias)).toEqual([
      'churn',
      'support',
      'crm',
      'social',
    ]);
  });

  test('should reject an unknown alias when checking room ids', () => {
    expect(isLabRoomAlias('churn')).toBe(true);
    expect(isLabRoomAlias('unknown')).toBe(false);
    expect(getLabRoom('unknown')).toBeUndefined();
  });

  test('should keep only CSV contract tables when rooms are listed', () => {
    const tables = LAB_ROOMS.flatMap((room) => room.tables);
    expect(tables.some((table) => table.includes('Topic_group'))).toBe(false);
    expect(tables.some((table) => table.includes('metadata'))).toBe(false);
    expect(getLabRoom('churn')?.tables).toContain(
      'workspace.ravenstack.ravenstack_churn_events',
    );
  });

  test('should mark a room configured only when the env key is set', () => {
    const rooms = listConfiguredLabRooms({
      GENIE_SPACE_ID_CHURN: 'space-churn',
    });
    expect(rooms.find((room) => room.alias === 'churn')?.spaceId).toBe(
      'space-churn',
    );
    expect(rooms.find((room) => room.alias === 'support')?.spaceId).toBeNull();
  });
});
