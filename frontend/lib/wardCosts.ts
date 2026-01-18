const MANA_COLORS = new Set(['W', 'U', 'B', 'R', 'G']);
const WARD_SEPARATORS = ['-', '—', ':'];

const extractManaSymbols = (text: string): string[] => {
  if (!text) return [];
  const symbols: string[] = [];
  let index = 0;
  while (index < text.length) {
    if (text[index] !== '{') {
      index += 1;
      continue;
    }
    const end = text.indexOf('}', index + 1);
    if (end === -1) break;
    const symbol = text.slice(index + 1, end);
    if (symbol) symbols.push(symbol);
    index = end + 1;
  }
  return symbols;
};

const isDigits = (value: string) => {
  if (!value) return false;
  for (let i = 0; i < value.length; i += 1) {
    const code = value.charCodeAt(i);
    if (code < 48 || code > 57) return false;
  }
  return true;
};

const isAlphaNumeric = (char: string) => {
  if (!char) return false;
  const code = char.charCodeAt(0);
  return (code >= 48 && code <= 57) || (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
};

const tokenize = (text: string) => {
  const tokens: string[] = [];
  let current = '';
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (isAlphaNumeric(char)) {
      current += char;
    } else if (current) {
      tokens.push(current);
      current = '';
    }
  }
  if (current) tokens.push(current);
  return tokens;
};

export type ManaCostData = {
  generic: number;
  colored: Record<string, number>;
  hybrids: Array<[string, string]>;
  two_brids: Array<[number, string]>;
  phyrexian: string[];
  colorless: number;
  x: number;
};

export type WardCost =
  | { type: 'mana'; cost: ManaCostData }
  | { type: 'life'; amount: number }
  | { type: 'discard'; amount: number }
  | { type: 'sacrifice'; cardType?: string; nonland?: boolean }
  | { type: 'tap'; cardType?: string; nonland?: boolean };

export const parseManaCostSymbols = (costText: string): ManaCostData => {
  const result: ManaCostData = {
    generic: 0,
    colored: {},
    hybrids: [],
    two_brids: [],
    phyrexian: [],
    colorless: 0,
    x: 0,
  };
  if (!costText) {
    return result;
  }
  const symbols = extractManaSymbols(costText).map((symbol) => symbol?.toUpperCase());
  symbols.forEach((symbol) => {
    if (!symbol) return;
    if (isDigits(symbol)) {
      result.generic += Number(symbol);
      return;
    }
    if (symbol === 'X') {
      result.x += 1;
      return;
    }
    if (symbol === 'C' || symbol === 'S') {
      result.colorless += 1;
      return;
    }
    if (MANA_COLORS.has(symbol)) {
      result.colored[symbol] = (result.colored[symbol] ?? 0) + 1;
      return;
    }
    if (symbol.includes('/')) {
      const parts = symbol.split('/');
      if (parts.length === 2 && parts[1] === 'P' && MANA_COLORS.has(parts[0])) {
        result.phyrexian.push(parts[0]);
        return;
      }
      if (parts.length === 2 && isDigits(parts[0]) && MANA_COLORS.has(parts[1])) {
        result.two_brids.push([Number(parts[0]), parts[1]]);
        return;
      }
      if (parts.length === 2 && MANA_COLORS.has(parts[0]) && MANA_COLORS.has(parts[1])) {
        result.hybrids.push([parts[0], parts[1]]);
        return;
      }
    }
  });
  return result;
};

export const serializeManaCostSymbols = (cost: ManaCostData): string => {
  const parts: string[] = [];
  const xCount = Number(cost.x || 0);
  for (let i = 0; i < xCount; i += 1) parts.push('{X}');
  const generic = Number(cost.generic || 0);
  if (generic > 0) parts.push(`{${generic}}`);
  const colors = ['W', 'U', 'B', 'R', 'G'];
  colors.forEach((color) => {
    const amount = Number(cost.colored?.[color] || 0);
    for (let i = 0; i < amount; i += 1) {
      parts.push(`{${color}}`);
    }
  });
  const colorless = Number(cost.colorless || 0);
  for (let i = 0; i < colorless; i += 1) parts.push('{C}');
  (cost.hybrids ?? []).forEach(([colorA, colorB]) => parts.push(`{${colorA}/${colorB}}`));
  (cost.two_brids ?? []).forEach(([genericValue, color]) => parts.push(`{${genericValue}/${color}}`));
  (cost.phyrexian ?? []).forEach((color) => parts.push(`{${color}/P}`));
  return parts.join('');
};

const normalizeWardText = (keyword: string) => {
  const lower = keyword.toLowerCase();
  if (!lower.startsWith('ward')) return '';
  const firstSeparator = WARD_SEPARATORS
    .map((sep) => keyword.indexOf(sep))
    .filter((index) => index >= 0)
    .sort((a, b) => a - b)[0];
  if (typeof firstSeparator === 'number') {
    return keyword.slice(firstSeparator + 1).trim();
  }
  if (lower.startsWith('ward')) {
    let index = 4;
    while (index < keyword.length && keyword[index] === ' ') {
      index += 1;
    }
    return keyword.slice(index).trim();
  }
  return '';
};

const normalizeCardType = (raw?: string | null) => {
  if (!raw) return undefined;
  const trimmed = raw.trim().toLowerCase();
  if (!trimmed) return undefined;
  if (trimmed === 'permanent') return undefined;
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
};

export const parseWardCosts = (keywords: string[]): WardCost[] => {
  const costs: WardCost[] = [];
  keywords.forEach((keyword) => {
    if (typeof keyword !== 'string') return;
    if (!keyword.toLowerCase().startsWith('ward')) return;
    const symbols = extractManaSymbols(keyword);
    if (symbols.length > 0) {
      const costText = symbols.map((symbol) => `{${symbol}}`).join('');
      costs.push({ type: 'mana', cost: parseManaCostSymbols(costText) });
      return;
    }
    const text = normalizeWardText(keyword);
    if (!text) return;
    const lower = text.toLowerCase();
    const tokens = tokenize(lower);
    for (let i = 0; i < tokens.length - 2; i += 1) {
      if (tokens[i] === 'pay' && tokens[i + 2] === 'life') {
        const amount = Number(tokens[i + 1]);
        if (Number.isFinite(amount)) {
          costs.push({ type: 'life', amount });
          return;
        }
      }
    }
    if (tokens.includes('discard')) {
      const index = tokens.indexOf('discard');
      const next = tokens[index + 1];
      const amount = Number(next);
      if (Number.isFinite(amount)) {
        costs.push({ type: 'discard', amount });
        return;
      }
      if (lower.includes('discard a card')) {
        costs.push({ type: 'discard', amount: 1 });
        return;
      }
    }
    if (tokens.includes('sacrifice')) {
      let index = tokens.indexOf('sacrifice') + 1;
      if (tokens[index] === 'a' || tokens[index] === 'an') index += 1;
      const nonland = tokens[index] === 'nonland';
      if (nonland) index += 1;
      const cardType = normalizeCardType(tokens[index]);
      costs.push({ type: 'sacrifice', cardType, nonland });
      return;
    }
    if (tokens.includes('tap')) {
      let index = tokens.indexOf('tap') + 1;
      if (tokens[index] === 'a' || tokens[index] === 'an') index += 1;
      const nonland = tokens[index] === 'nonland';
      if (nonland) index += 1;
      const cardType = normalizeCardType(tokens[index]);
      costs.push({ type: 'tap', cardType, nonland });
      return;
    }
  });
  return costs;
};

export const formatManaCostLabel = (cost: ManaCostData): string => {
  const parts: string[] = [];
  const xCount = Number(cost.x || 0);
  if (xCount > 0) parts.push(`${xCount}X`);
  Object.entries(cost.colored ?? {}).forEach(([color, amount]) => {
    const count = Number(amount || 0);
    if (count > 0) parts.push(`${count}${color}`);
  });
  if (cost.colorless) parts.push(`${cost.colorless}C`);
  if (cost.generic) parts.push(`${cost.generic}`);
  if (cost.hybrids?.length || cost.phyrexian?.length || cost.two_brids?.length) {
    parts.push('hybrid/phyrexian');
  }
  return parts.join(' + ') || '0';
};

