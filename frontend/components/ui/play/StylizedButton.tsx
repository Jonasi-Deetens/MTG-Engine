import React from 'react';
import { Button } from '@/components/ui/Button';

type StylizedButtonVariant = 'primary' | 'secondary' | 'ghost';

const variantMap: Record<StylizedButtonVariant, 'nier-primary' | 'nier-secondary' | 'nier-ghost'> = {
  primary: 'nier-primary',
  secondary: 'nier-secondary',
  ghost: 'nier-ghost',
};

export function StylizedButton({
  variant = 'primary',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: StylizedButtonVariant }) {
  return <Button variant={variantMap[variant]} {...props} />;
}
