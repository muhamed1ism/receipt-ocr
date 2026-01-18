import { Control, FieldValues, Path } from "react-hook-form";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { Input } from "../ui/input";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface NumberFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  inputClassName?: string;
  className?: string;
  editMode: boolean | string;
  disabled?: boolean;
  onChange?: (value: number | undefined) => void;
  prepend?: string;
  append?: string;
}

export default function NumberFormField<T extends FieldValues>({
  name,
  control,
  label,
  inputClassName,
  className,
  editMode,
  disabled = false,
  onChange,
  prepend,
  append,
}: NumberFormFieldProps<T>) {
  const [textValue, setTextValue] = useState<string | undefined>(undefined);

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) =>
        editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <div className="flex flex-row gap-2 items-center">
                {prepend && <span className="text-md">{prepend}</span>}
                <Input
                  type="text"
                  inputMode="numeric"
                  disabled={disabled}
                  className={cn(
                    "shadow-none font-normal font-sans text-end",
                    inputClassName,
                  )}
                  // Show textValue if defined, else show field.value
                  value={
                    textValue !== undefined ? textValue : (field.value ?? "")
                  }
                  onChange={(e) => {
                    const value = e.target.value;

                    // Allow empty or digits only (no decimals)
                    if (!/^\d*$/.test(value)) return;

                    setTextValue(value);

                    if (value === "") {
                      field.onChange(undefined);
                      onChange?.(undefined);
                      return;
                    }

                    const num = Number(value);
                    if (!Number.isNaN(num) && num !== 0) {
                      field.onChange(num);
                      onChange?.(num);
                    }
                  }}
                />
                {append && <span className="text-md">{append}</span>}
              </div>
            </FormControl>
            <FormMessage />
          </FormItem>
        ) : (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <div className="flex flex-row gap-2 items-center">
              {prepend && <span className="text-md">{prepend}</span>}
              <p
                className={cn(
                  "py-2 truncate max-w-sm font-normal font-sans text-end",
                  field.value === undefined && "text-muted-foreground",
                  className,
                )}
              >
                {field.value ?? "N/A"}
              </p>
              {append && <span className="text-md">{append}</span>}
            </div>
          </FormItem>
        )
      }
    />
  );
}
