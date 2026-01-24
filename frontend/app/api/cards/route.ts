// frontend/app/api/cards/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = searchParams.get('page') || '1';
    const page_size = searchParams.get('page_size') || '20';
    const colors = searchParams.get('colors');
    const types = searchParams.get('types') || searchParams.get('type');
    const set_code = searchParams.get('set_code');
    const rarity = searchParams.get('rarity');
    const lang = searchParams.get('lang');
    const keywords = searchParams.get('keywords');
    const color_identity = searchParams.get('color_identity');
    const supertypes = searchParams.get('supertypes');
    const subtypes = searchParams.get('subtypes');
    const layout = searchParams.get('layout');
    const produced_mana = searchParams.get('produced_mana');
    const cmc_min = searchParams.get('cmc_min');
    const cmc_max = searchParams.get('cmc_max');
    const power_min = searchParams.get('power_min');
    const power_max = searchParams.get('power_max');
    const toughness_min = searchParams.get('toughness_min');
    const toughness_max = searchParams.get('toughness_max');
    const loyalty_min = searchParams.get('loyalty_min');
    const loyalty_max = searchParams.get('loyalty_max');
    const is_legendary = searchParams.get('is_legendary');
    
    // Build URL with filter parameters
    const urlParams = new URLSearchParams();
    urlParams.set('page', page);
    urlParams.set('page_size', page_size);
    if (colors) urlParams.set('colors', colors);
    if (types) urlParams.set('types', types);
    if (set_code) urlParams.set('set_code', set_code);
    if (rarity) urlParams.set('rarity', rarity);
    if (lang) urlParams.set('lang', lang);
    if (keywords) urlParams.set('keywords', keywords);
    if (color_identity) urlParams.set('color_identity', color_identity);
    if (supertypes) urlParams.set('supertypes', supertypes);
    if (subtypes) urlParams.set('subtypes', subtypes);
    if (layout) urlParams.set('layout', layout);
    if (produced_mana) urlParams.set('produced_mana', produced_mana);
    if (cmc_min) urlParams.set('cmc_min', cmc_min);
    if (cmc_max) urlParams.set('cmc_max', cmc_max);
    if (power_min) urlParams.set('power_min', power_min);
    if (power_max) urlParams.set('power_max', power_max);
    if (toughness_min) urlParams.set('toughness_min', toughness_min);
    if (toughness_max) urlParams.set('toughness_max', toughness_max);
    if (loyalty_min) urlParams.set('loyalty_min', loyalty_min);
    if (loyalty_max) urlParams.set('loyalty_max', loyalty_max);
    if (is_legendary) urlParams.set('is_legendary', is_legendary);
    
    const url = `${API_URL}/api/cards?${urlParams.toString()}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to list cards', cards: [], total: 0, page: 1, page_size: 20, has_more: false },
      { status: 500 }
    );
  }
}

