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

interface TextFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  editMode: boolean | string;
  inputClassName?: string;
  className?: string;
}

export default function TextFormField<T extends FieldValues>({
  name,
  control,
  label,
  editMode,
  inputClassName,
  className,
}: TextFormFieldProps<T>) {
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
                className={cn(
                  "shadow-none font-normal font-sans",
                  inputClassName,
                )}
                {...field}
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
                !field.value && "text-muted-foreground",
                className,
              )}
            >
              {field.value || "N/A"}
            </p>
          </FormItem>
        )
      }
    />
  );
}
