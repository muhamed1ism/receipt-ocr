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

interface NumberFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  editMode: boolean | string;
  disabled?: boolean;
  onChange?: (value: number) => void;
}

export default function NumberFormField<T extends FieldValues>({
  name,
  control,
  label,
  editMode,
  disabled = false,
  onChange,
}: NumberFormFieldProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) =>
        editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <Input
                type="text"
                inputMode="decimal"
                disabled={disabled}
                className="font-normal font-sans"
                {...field}
                onChange={(e) => {
                  field.onChange(e.target.value); 
                  if (onChange) onChange(parseFloat(e.target.value) || 0);
                }}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        ) : (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <p
              className={cn(
                "py-2 truncate max-w-sm font-normal font-sans",
                field.value === undefined && "text-muted-foreground"
              )}
            >
              {field.value ?? "N/A"}
            </p>
          </FormItem>
        )
      }
    />
  );
}
