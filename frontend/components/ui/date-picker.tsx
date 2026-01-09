import * as React from "react";
import { cn } from "@/lib/utils";
import { Calendar } from "lucide-react";
import { Input } from "./input";

export interface DatePickerProps {
  value?: Date | string;
  onChange?: (date: Date | null) => void;
  placeholder?: string;
  min?: Date | string;
  max?: Date | string;
  disabled?: boolean;
  className?: string;
  label?: string;
  error?: string;
}

export function DatePicker({
  value,
  onChange,
  placeholder = "Select date",
  min,
  max,
  disabled,
  className,
  label,
  error,
}: DatePickerProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);

  const formatDate = (date: Date | string | undefined): string => {
    if (!date) return "";
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toISOString().split("T")[0];
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dateString = e.target.value;
    if (dateString) {
      const date = new Date(dateString);
      onChange?.(date);
    } else {
      onChange?.(null);
    }
  };

  return (
    <div className={cn("w-full", className)}>
      {label && (
        <label className="block text-sm font-medium text-foreground mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <Input
          ref={inputRef}
          type="date"
          value={formatDate(value)}
          onChange={handleDateChange}
          min={formatDate(min)}
          max={formatDate(max)}
          disabled={disabled}
          className={cn(
            "pr-10",
            error && "border-destructive focus-visible:ring-destructive"
          )}
          placeholder={placeholder}
        />
        <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
      </div>
      {error && (
        <p className="mt-1 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}






