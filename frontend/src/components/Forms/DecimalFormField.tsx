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

interface DecimalFormFieldProps<T extends FieldValues> {
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

export default function DecimalFormField<T extends FieldValues>({
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
}: DecimalFormFieldProps<T>) {
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
                  inputMode="decimal"
                  disabled={disabled}
                  className={cn(
                    "shadow-none font-normal font-sans text-end",
                    inputClassName,
                  )}
                  // Show textValue if it's defined, otherwise show field.value
                  value={
                    textValue !== undefined ? textValue : (field.value ?? "")
                  }
                  onChange={(e) => {
                    const value = e.target.value;

                    // allow empty, digits, one dot
                    if (!/^\d*\.?\d*$/.test(value)) return;

                    setTextValue(value);

                    if (value === "" || value === ".") {
                      field.onChange(undefined);
                      onChange?.(undefined);
                      return;
                    }

                    const num = Number(value);
                    if (!Number.isNaN(num)) {
                      field.onChange(num); // RHF gets number ✅
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
