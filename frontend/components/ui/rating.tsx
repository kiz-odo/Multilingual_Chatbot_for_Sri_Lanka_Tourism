import * as React from "react";
import { cn } from "@/lib/utils";
import { Star } from "lucide-react";

export interface RatingProps {
  value: number;
  max?: number;
  onChange?: (value: number) => void;
  readonly?: boolean;
  size?: "sm" | "md" | "lg";
  showValue?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-6 w-6",
};

export function Rating({
  value,
  max = 5,
  onChange,
  readonly = false,
  size = "md",
  showValue = false,
  className,
}: RatingProps) {
  const [hoverValue, setHoverValue] = React.useState<number | null>(null);
  const displayValue = hoverValue !== null ? hoverValue : value;

  return (
    <div className={cn("flex items-center space-x-1", className)}>
      {Array.from({ length: max }).map((_, index) => {
        const starValue = index + 1;
        const isFilled = starValue <= displayValue;

        return (
          <button
            key={index}
            type="button"
            onClick={() => !readonly && onChange?.(starValue)}
            onMouseEnter={() => !readonly && setHoverValue(starValue)}
            onMouseLeave={() => !readonly && setHoverValue(null)}
            disabled={readonly}
            className={cn(
              "transition-colors",
              readonly ? "cursor-default" : "cursor-pointer hover:scale-110"
            )}
            aria-label={`Rate ${starValue} out of ${max}`}
          >
            <Star
              className={cn(
                sizeClasses[size],
                isFilled
                  ? "fill-yellow-400 text-yellow-400"
                  : "text-muted"
              )}
            />
          </button>
        );
      })}
      {showValue && (
        <span className="ml-2 text-sm font-medium text-muted-foreground">
          {value.toFixed(1)}
        </span>
      )}
    </div>
  );
}







