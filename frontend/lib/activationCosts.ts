import { parseManaCostSymbols, formatManaCostLabel } from '@/lib/wardCosts';

const MANA_SYMBOL_PATTERN = /\{([^}]+)\}/g;
const SEPARATOR_PATTERN = /[,;]/;

export type ActivationCost =
  | { type: 'mana'; costText: string; cost: ReturnType<typeof parseManaCostSymbols> }
  | { type: 'tap_self' }
  | { type: 'life'; amount: number }
  | { type: 'discard'; amount: number }
  | { type: 'sacrifice'; cardType?: string; nonland?: boolean }
  | { type: 'sacrifice_self' }
  | { type: 'tap'; cardType?: string; nonland?: boolean };

const normalizeCardType = (raw?: string | null) => {
  if (!raw) return undefined;
  const trimmed = raw.trim().toLowerCase();
  if (!trimmed || trimmed === 'permanent' || trimmed === 'permanents') return undefined;
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
};

const parseTextCost = (text: string): ActivationCost[] => {
  const lower = text.toLowerCase().trim();
  if (!lower) return [];
  const lifeMatch = lower.match(/pay\s+(\d+)\s+life/);
  if (lifeMatch) {
    return [{ type: 'life', amount: Number(lifeMatch[1]) }];
  }
  const discardMatch = lower.match(/discard\s+(\d+)\s+cards?/);
  if (discardMatch) {
    return [{ type: 'discard', amount: Number(discardMatch[1]) }];
  }
  if (lower.includes('discard a card')) {
    return [{ type: 'discard', amount: 1 }];
  }
  if (lower.includes('sacrifice this') || lower.includes('sacrifice ~') || lower.includes('sacrifice it')) {
    return [{ type: 'sacrifice_self' }];
  }
  const sacrificeMatch = lower.match(/sacrifice\s+(?:a|an)?\s*(nonland\s+)?([a-z]+)?/);
  if (sacrificeMatch) {
    return [{
      type: 'sacrifice',
      nonland: !!sacrificeMatch[1],
      cardType: normalizeCardType(sacrificeMatch[2]),
    }];
  }
  if (lower.includes('tap this') || lower.includes('tap ~') || lower === 'tap') {
    return [{ type: 'tap_self' }];
  }
  const tapMatch = lower.match(/tap\s+(?:an|a)?\s*(untapped\s+)?(nonland\s+)?([a-z]+)?/);
  if (tapMatch) {
    return [{
      type: 'tap',
      nonland: !!tapMatch[2],
      cardType: normalizeCardType(tapMatch[3]),
    }];
  }
  return [];
};

export const parseActivationCosts = (costText: string): ActivationCost[] => {
  if (!costText) return [];
  const segments = costText.split(SEPARATOR_PATTERN).map((segment) => segment.trim()).filter(Boolean);
  const costs: ActivationCost[] = [];
  segments.forEach((segment) => {
    const symbols = [...segment.matchAll(MANA_SYMBOL_PATTERN)].map((match) => match[1]?.toUpperCase()).filter(Boolean);
    if (symbols.length > 0) {
      const manaSymbols: string[] = [];
      symbols.forEach((symbol) => {
        if (symbol === 'T') {
          costs.push({ type: 'tap_self' });
        } else {
          manaSymbols.push(symbol);
        }
      });
      if (manaSymbols.length > 0) {
        const manaText = manaSymbols.map((symbol) => `{${symbol}}`).join('');
        costs.push({ type: 'mana', costText: manaText, cost: parseManaCostSymbols(manaText) });
      }
      return;
    }
    costs.push(...parseTextCost(segment));
  });
  return costs;
};

export const formatActivationCostLabel = (cost: ActivationCost) => {
  if (cost.type === 'mana') return formatManaCostLabel(cost.cost);
  if (cost.type === 'life') return `pay ${cost.amount} life`;
  if (cost.type === 'discard') return `discard ${cost.amount} card${cost.amount === 1 ? '' : 's'}`;
  if (cost.type === 'sacrifice') return `sacrifice ${cost.nonland ? 'nonland ' : ''}${cost.cardType ?? 'permanent'}`;
  if (cost.type === 'sacrifice_self') return 'sacrifice this';
  if (cost.type === 'tap') return `tap ${cost.nonland ? 'nonland ' : ''}${cost.cardType ?? 'permanent'}`;
  if (cost.type === 'tap_self') return 'tap this';
  return 'cost';
};

export const extractAdditionalCastCostText = (oracleText?: string | null) => {
  if (!oracleText) return '';
  const lines = oracleText.split('\n');
  for (const line of lines) {
    const match = line.match(/additional cost to cast[^,]*,\s*(.+)/i);
    if (match?.[1]) {
      const raw = match[1].split('.').shift() ?? '';
      return raw.trim();
    }
  }
  return '';
};

export type AlternativeCostOption = {
  tag: string;
  label: string;
};

export const parseAlternativeCastCosts = (oracleText?: string | null): AlternativeCostOption[] => {
  if (!oracleText) return [];
  const options: AlternativeCostOption[] = [];
  const lines = oracleText.split('\n');
  lines.forEach((line) => {
    const flashback = line.match(/flashback\s+(\{[^}]+\}(?:\{[^}]+\})*)/i);
    if (flashback?.[1]) {
      const costText = flashback[1];
      options.push({ tag: `flashback:${costText}`, label: `Flashback ${costText}` });
    }
    const escape = line.match(/escape\s+(\{[^}]+\}(?:\{[^}]+\})*)/i);
    if (escape?.[1]) {
      const costText = escape[1];
      options.push({ tag: `escape:${costText}`, label: `Escape ${costText}` });
    }
    if (/jump-start/i.test(line)) {
      options.push({ tag: 'jump-start', label: 'Jump-start' });
    }
    if (/without paying its mana cost/i.test(line)) {
      options.push({ tag: 'free', label: 'Without paying its mana cost' });
    }
    const match = line.match(/you may cast this spell for\s+(\{[^}]+\}(?:\{[^}]+\})*)/i);
    if (match?.[1]) {
      const costText = match[1];
      options.push({ tag: costText, label: `Pay ${costText}` });
    }
  });
  return options;
};

export const parseAlternativeExtraCosts = (oracleText?: string | null, tag?: string | null) => {
  if (!oracleText || !tag) return '';
  if (tag === 'jump-start') {
    return 'discard a card';
  }
  if (tag.startsWith('escape')) {
    const lines = oracleText.split('\n');
    for (const line of lines) {
      if (!/escape/i.test(line)) continue;
      const parts = line.split('—');
      if (parts.length > 1) {
        return parts[1].trim().split('.').shift() ?? '';
      }
      const dashParts = line.split('-');
      if (dashParts.length > 1) {
        return dashParts.slice(1).join('-').trim().split('.').shift() ?? '';
      }
    }
  }
  return '';
};

