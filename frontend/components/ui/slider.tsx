import * as React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps {
  value?: number[];
  defaultValue?: number[];
  min?: number;
  max?: number;
  step?: number;
  onChange?: (value: number[]) => void;
  disabled?: boolean;
  className?: string;
  label?: string;
}

export function Slider({
  value: controlledValue,
  defaultValue = [0],
  min = 0,
  max = 100,
  step = 1,
  onChange,
  disabled,
  className,
  label,
}: SliderProps) {
  const [internalValue, setInternalValue] = React.useState(defaultValue);
  const value = controlledValue !== undefined ? controlledValue : internalValue;
  const currentValue = value[0] || 0;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = [Number(e.target.value)];
    if (controlledValue === undefined) {
      setInternalValue(newValue);
    }
    onChange?.(newValue);
  };

  const percentage = ((currentValue - min) / (max - min)) * 100;

  return (
    <div className={cn("w-full", className)}>
      {label && (
        <label className="block text-sm font-medium text-foreground mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={currentValue}
          onChange={handleChange}
          disabled={disabled}
          className={cn(
            "w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer",
            "accent-primary",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          style={{
            background: `linear-gradient(to right, hsl(var(--primary)) 0%, hsl(var(--primary)) ${percentage}%, hsl(var(--muted)) ${percentage}%, hsl(var(--muted)) 100%)`,
          }}
        />
        <div className="flex justify-between mt-2 text-xs text-muted-foreground">
          <span>{min}</span>
          <span className="font-medium text-foreground">{currentValue}</span>
          <span>{max}</span>
        </div>
      </div>
    </div>
  );
}






