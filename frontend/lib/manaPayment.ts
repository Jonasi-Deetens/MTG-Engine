export type ManaPaymentDetail = {
  hybrid_choices: string[];
  two_brid_choices: boolean[];
  phyrexian_choices: boolean[];
};

export const hasComplexManaCost = (cost: any) =>
  !!(
    (cost?.hybrids && cost.hybrids.length) ||
    (cost?.two_brids && cost.two_brids.length) ||
    (cost?.phyrexian && cost.phyrexian.length)
  );

export const buildDefaultManaPayment = (cost: any, pool: Record<string, number>) => {
  if (!cost) return {};
  if (hasComplexManaCost(cost)) {
    return {};
  }
  const payment: Record<string, number> = {};
  const remainingPool: Record<string, number> = { ...pool };

  Object.entries(cost.colored ?? {}).forEach(([color, amount]) => {
    const available = remainingPool[color] ?? 0;
    const spend = Math.min(available, Number(amount) || 0);
    if (spend > 0) {
      payment[color] = spend;
      remainingPool[color] = available - spend;
    }
  });

  if (cost.colorless) {
    const available = remainingPool.C ?? 0;
    const spend = Math.min(available, Number(cost.colorless) || 0);
    if (spend > 0) {
      payment.C = (payment.C ?? 0) + spend;
      remainingPool.C = available - spend;
    }
  }

  let genericRemaining = Number(cost.generic) || 0;
  Object.entries(remainingPool).forEach(([color, amount]) => {
    if (genericRemaining <= 0) return;
    const spend = Math.min(amount, genericRemaining);
    if (spend > 0) {
      payment[color] = (payment[color] ?? 0) + spend;
      genericRemaining -= spend;
    }
  });

  return payment;
};

export const buildDefaultPaymentDetail = (cost: any, pool: Record<string, number>): ManaPaymentDetail => {
  const hybrid_choices =
    cost?.hybrids?.map(([colorA, colorB]: [string, string]) =>
      (pool[colorA] ?? 0) > 0 ? colorA : colorB
    ) ?? [];
  const two_brid_choices =
    cost?.two_brids?.map(([_genericValue, color]: [number, string]) => (pool[color] ?? 0) > 0) ?? [];
  const phyrexian_choices =
    cost?.phyrexian?.map((color: string) => (pool[color] ?? 0) === 0) ?? [];
  return { hybrid_choices, two_brid_choices, phyrexian_choices };
};

export const buildPaymentFromDetail = (
  cost: any,
  pool: Record<string, number>,
  detail: ManaPaymentDetail
) => {
  if (!cost) return { payment: {}, errors: [] as string[] };
  const errors: string[] = [];
  const payment: Record<string, number> = {};
  const remainingPool: Record<string, number> = { ...pool };

  const colored = cost.colored ?? {};
  Object.entries(colored).forEach(([color, amount]) => {
    const available = remainingPool[color] ?? 0;
    const required = Number(amount) || 0;
    if (available < required) {
      errors.push(`Missing required ${color} mana.`);
      return;
    }
    if (required > 0) {
      payment[color] = (payment[color] ?? 0) + required;
      remainingPool[color] = available - required;
    }
  });

  (cost.hybrids ?? []).forEach(([colorA, colorB]: [string, string], index: number) => {
    const choice = detail.hybrid_choices[index];
    if (choice !== colorA && choice !== colorB) {
      errors.push('Invalid hybrid choice.');
      return;
    }
    const available = remainingPool[choice] ?? 0;
    if (available <= 0) {
      errors.push(`Not enough ${choice} mana for hybrid cost.`);
      return;
    }
    payment[choice] = (payment[choice] ?? 0) + 1;
    remainingPool[choice] = available - 1;
  });

  let genericRequired = Number(cost.generic) || 0;

  (cost.two_brids ?? []).forEach(([genericValue, color]: [number, string], index: number) => {
    const payColor = detail.two_brid_choices[index];
    if (payColor) {
      const available = remainingPool[color] ?? 0;
      if (available <= 0) {
        errors.push(`Not enough ${color} mana for two-brid cost.`);
        return;
      }
      payment[color] = (payment[color] ?? 0) + 1;
      remainingPool[color] = available - 1;
    } else {
      genericRequired += Number(genericValue) || 0;
    }
  });

  (cost.phyrexian ?? []).forEach((color: string, index: number) => {
    const payLife = detail.phyrexian_choices[index];
    if (payLife) {
      return;
    }
    const available = remainingPool[color] ?? 0;
    if (available <= 0) {
      errors.push(`Not enough ${color} mana for phyrexian cost.`);
      return;
    }
    payment[color] = (payment[color] ?? 0) + 1;
    remainingPool[color] = available - 1;
  });

  const colorlessRequired = Number(cost.colorless) || 0;
  const availableColorless = remainingPool.C ?? 0;
  if (availableColorless < colorlessRequired) {
    errors.push('Missing required colorless mana.');
  } else if (colorlessRequired > 0) {
    payment.C = (payment.C ?? 0) + colorlessRequired;
    remainingPool.C = availableColorless - colorlessRequired;
  }

  Object.entries(remainingPool).forEach(([color, amount]) => {
    if (genericRequired <= 0) return;
    const spend = Math.min(amount, genericRequired);
    if (spend > 0) {
      payment[color] = (payment[color] ?? 0) + spend;
      genericRequired -= spend;
    }
  });

  if (genericRequired > 0) {
    errors.push('Not enough mana selected to cover the cost.');
  }

  return { payment, errors };
};

export const getManaPaymentErrors = (
  cost: any,
  payment: Record<string, number>,
  pool: Record<string, number>
) => {
  if (!cost) return { errors: [] as string[], totalRequired: 0 };
  if (hasComplexManaCost(cost)) {
    return { errors: ['Hybrid/phyrexian costs require auto-pay.'], totalRequired: 0 };
  }
  const errors: string[] = [];
  const totalRequired =
    (Number(cost.generic) || 0) +
    (Number(cost.colorless) || 0) +
    Object.values(cost.colored ?? {}).reduce((sum: number, amount: any) => sum + Number(amount || 0), 0);
  const totalPaid = Object.values(payment).reduce((sum, amount) => sum + (Number(amount) || 0), 0);
  if (totalPaid < totalRequired) {
    errors.push('Not enough mana selected to cover the cost.');
  }
  Object.entries(cost.colored ?? {}).forEach(([color, amount]) => {
    if ((payment[color] ?? 0) < Number(amount || 0)) {
      errors.push(`Missing required ${color} mana.`);
    }
  });
  if ((payment.C ?? 0) < Number(cost.colorless || 0)) {
    errors.push('Missing required colorless mana.');
  }
  Object.entries(payment).forEach(([color, amount]) => {
    if ((pool[color] ?? 0) < Number(amount || 0)) {
      errors.push(`Overpaid ${color} mana (exceeds pool).`);
    }
  });
  return { errors, totalRequired };
};

