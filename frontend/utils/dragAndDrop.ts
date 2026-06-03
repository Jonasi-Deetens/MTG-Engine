// frontend/utils/dragAndDrop.ts

/**
 * Extract card ID from drag ID (format: "card-{card_id}")
 */
export function extractCardId(dragId: string): string | null {
  if (dragId.startsWith('card-')) {
    return dragId.replace('card-', '');
  }
  return null;
}

/**
 * Extract list ID from drop ID (format: "list-{list_id}")
 */
export function extractListId(dropId: string): number | null {
  if (dropId.startsWith('list-')) {
    const id = parseInt(dropId.replace('list-', ''), 10);
    return isNaN(id) ? null : id;
  }
  return null;
}

/**
 * Extract type from drop ID (format: "type-{type}")
 */
export function extractType(dropId: string): string | null {
  if (dropId.startsWith('type-')) {
    return dropId.replace('type-', '');
  }
  return null;
}

/**
 * Check if drop ID is a commander list
 */
export function isCommanderList(dropId: string): boolean {
  return dropId === 'commander-list';
}

