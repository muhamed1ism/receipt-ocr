import { cn } from "@/lib/utils";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Control, FieldValues, Path } from "react-hook-form";

export interface OptionType {
  label: string;
  value: string;
}

interface SelectFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  editMode: boolean | string;
  options: OptionType[];
}

export default function SelectFormField<T extends FieldValues>({
  name,
  control,
  label,
  editMode,
  options,
}: SelectFormFieldProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) =>
        editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <Select {...field} onValueChange={field.onChange}>
                <SelectTrigger className="flex font-sans border-0 border-b-2 border-dashed border-foreground/50 bg-transparent dark:bg-accent rounded-none shadow-none data-[state=open]:border-foreground">
                  <SelectValue placeholder="odaberi valutu" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {options.map((option, index) => (
                      <SelectItem key={index} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
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
