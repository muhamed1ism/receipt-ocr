import { cn } from "@/lib/utils";
import { DatePicker } from "../ui/date-picker";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { formatDate } from "@/utils/formatDateTime";
import { Control, FieldValues, Path } from "react-hook-form";

interface DateFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  inputClassName?: string;
  className?: string;
  editMode?: boolean | string;
}

export default function DateFormField<T extends FieldValues>({
  name,
  control,
  label,
  inputClassName,
  className,
  editMode = "disabled",
}: DateFormFieldProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) =>
        editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <DatePicker
                className={cn(inputClassName)}
                dateValue={field.value}
                setDateValue={field.onChange}
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
              {field.value ? formatDate(field.value) : "N/A"}
            </p>
          </FormItem>
        )
      }
    />
  );
}
