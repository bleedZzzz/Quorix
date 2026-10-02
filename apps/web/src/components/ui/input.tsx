"use client";

import { forwardRef, type InputHTMLAttributes, useId } from "react";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, icon, id: externalId, ...props }, ref) => {
    const generatedId = useId();
    const id = externalId || generatedId;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label
            htmlFor={id}
            className="text-sm font-medium text-text-secondary"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center w-full">
          {icon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-text-muted">
              {icon}
            </div>
          )}
          <input
            id={id}
            ref={ref}
            className={cn(
              "h-9 w-full rounded-[var(--radius-md)] border bg-surface px-3 text-sm",
              icon && "pl-9",
              "text-text-primary placeholder:text-text-muted",
              "transition-colors duration-[var(--duration-fast)]",
              "focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              error
                ? "border-error focus:ring-error/40 focus:border-error"
                : "border-border hover:border-border-focus/40",
              className
            )}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
            {...props}
          />
        </div>
        {error && (
          <p id={`${id}-error`} className="text-xs text-error" role="alert">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={`${id}-hint`} className="text-xs text-text-muted">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input, type InputProps };
