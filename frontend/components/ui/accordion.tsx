import * as React from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

export interface AccordionProps {
  children: React.ReactNode;
  type?: "single" | "multiple";
  defaultValue?: string | string[];
  className?: string;
}

export interface AccordionItemProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export interface AccordionTriggerProps {
  children: React.ReactNode;
  className?: string;
}

export interface AccordionContentProps {
  children: React.ReactNode;
  className?: string;
}

const AccordionContext = React.createContext<{
  openItems: Set<string>;
  toggleItem: (value: string) => void;
  type: "single" | "multiple";
}>({
  openItems: new Set(),
  toggleItem: () => {},
  type: "single",
});

export function Accordion({
  children,
  type = "single",
  defaultValue,
  className,
}: AccordionProps) {
  const initialOpen = React.useMemo(() => {
    if (type === "single") {
      return new Set(defaultValue ? [defaultValue as string] : []);
    }
    return new Set(defaultValue as string[] || []);
  }, [defaultValue, type]);

  const [openItems, setOpenItems] = React.useState<Set<string>>(initialOpen);

  const toggleItem = React.useCallback(
    (value: string) => {
      setOpenItems((prev) => {
        const newSet = new Set(prev);
        if (newSet.has(value)) {
          newSet.delete(value);
        } else {
          if (type === "single") {
            return new Set([value]);
          }
          newSet.add(value);
        }
        return newSet;
      });
    },
    [type]
  );

  return (
    <AccordionContext.Provider value={{ openItems, toggleItem, type }}>
      <div className={cn("space-y-2", className)}>{children}</div>
    </AccordionContext.Provider>
  );
}

const AccordionItemContext = React.createContext<string>("");

export function AccordionItem({ value, children, className }: AccordionItemProps) {
  return (
    <AccordionItemContext.Provider value={value}>
      <div className={cn("border rounded-lg", className)}>{children}</div>
    </AccordionItemContext.Provider>
  );
}

export function AccordionTrigger({ children, className }: AccordionTriggerProps) {
  const { openItems, toggleItem } = React.useContext(AccordionContext);
  const parent = React.useContext(AccordionItemContext);
  const isOpen = openItems.has(parent);

  return (
    <button
      onClick={() => toggleItem(parent)}
      className={cn(
        "flex w-full items-center justify-between p-4 font-medium transition-all hover:bg-muted [&[data-state=open]>svg]:rotate-180",
        className
      )}
    >
      {children}
      <ChevronDown
        className={cn(
          "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
          isOpen && "rotate-180"
        )}
      />
    </button>
  );
}

export function AccordionContent({ children, className }: AccordionContentProps) {
  const { openItems } = React.useContext(AccordionContext);
  const parent = React.useContext(AccordionItemContext);
  const isOpen = openItems.has(parent);

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        "overflow-hidden text-sm transition-all data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down",
        className
      )}
    >
      <div className="p-4 pt-0">{children}</div>
    </div>
  );
}

