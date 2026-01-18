const MANA_SYMBOL_PATTERN = /\{([^}]+)\}/g;
const MANA_COLORS = new Set(['W', 'U', 'B', 'R', 'G']);
const WARD_SEPARATOR = /[-—:]/;

export type ParsedManaCost = {
  generic: number;
  colored: Record<string, number>;
  hybrids: Array<[string, string]>;
  two_brids: Array<[number, string]>;
  phyrexian: string[];
  colorless: number;
};

export type WardCost =
  | { type: 'mana'; costText: string; cost: ParsedManaCost }
  | { type: 'life'; amount: number }
  | { type: 'discard'; amount: number }
  | { type: 'sacrifice'; cardType?: string; nonland?: boolean }
  | { type: 'tap'; cardType?: string; nonland?: boolean };

export const parseManaCostSymbols = (costText: string): ParsedManaCost => {
  const result: ParsedManaCost = {
    generic: 0,
    colored: {},
    hybrids: [],
    two_brids: [],
    phyrexian: [],
    colorless: 0,
  };
  if (!costText) {
    return result;
  }
  const symbols = [...costText.matchAll(MANA_SYMBOL_PATTERN)].map((match) => match[1]?.toUpperCase());
  symbols.forEach((symbol) => {
    if (!symbol) return;
    if (/^\d+$/.test(symbol)) {
      result.generic += Number(symbol);
      return;
    }
    if (symbol === 'X') {
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
      if (parts.length === 2 && /^\d+$/.test(parts[0]) && MANA_COLORS.has(parts[1])) {
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

const normalizeWardText = (keyword: string) => {
  const lower = keyword.toLowerCase();
  if (!lower.startsWith('ward')) return '';
  const parts = keyword.split(WARD_SEPARATOR);
  if (parts.length > 1) {
    return parts.slice(1).join('-').trim();
  }
  return keyword.replace(/^ward\s*/i, '').trim();
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
    const symbols = [...keyword.matchAll(MANA_SYMBOL_PATTERN)].map((match) => match[1]);
    if (symbols.length > 0) {
      const costText = symbols.map((symbol) => `{${symbol}}`).join('');
      costs.push({ type: 'mana', costText, cost: parseManaCostSymbols(costText) });
      return;
    }
    const text = normalizeWardText(keyword);
    if (!text) return;
    const lower = text.toLowerCase();
    const lifeMatch = lower.match(/pay\s+(\d+)\s+life/);
    if (lifeMatch) {
      costs.push({ type: 'life', amount: Number(lifeMatch[1]) });
      return;
    }
    const discardMatch = lower.match(/discard\s+(\d+)\s+cards?/);
    if (discardMatch) {
      costs.push({ type: 'discard', amount: Number(discardMatch[1]) });
      return;
    }
    if (lower.includes('discard a card')) {
      costs.push({ type: 'discard', amount: 1 });
      return;
    }
    const sacrificeMatch = lower.match(/sacrifice\s+(a|an)?\s*(nonland\s+)?([a-z]+)?/);
    if (sacrificeMatch) {
      const nonland = !!sacrificeMatch[2];
      const cardType = normalizeCardType(sacrificeMatch[3]);
      costs.push({ type: 'sacrifice', cardType, nonland });
      return;
    }
    const tapMatch = lower.match(/tap\s+(an|a)?\s*(nonland\s+)?([a-z]+)?/);
    if (tapMatch) {
      const nonland = !!tapMatch[2];
      const cardType = normalizeCardType(tapMatch[3]);
      costs.push({ type: 'tap', cardType, nonland });
      return;
    }
  });
  return costs;
};

export const formatManaCostLabel = (cost: ParsedManaCost): string => {
  const parts: string[] = [];
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

