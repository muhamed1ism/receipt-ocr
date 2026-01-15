import { cn } from "@/lib/utils";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { formatTime } from "@/utils/formatDateTime";
import { Control, FieldValues, Path } from "react-hook-form";
import { Input } from "../ui/input";

interface TimeFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  editMode?: boolean | string;
}

export default function TimeFormField<T extends FieldValues>({
  name,
  control,
  label,
  editMode = "disabled",
}: TimeFormFieldProps<T>) {
  // TODO: Fix timezone

  const handleTimeChange = (
    onChange: (value: string) => void,
    fieldValue: string | undefined,
    part: "hours" | "minutes",
    value: string,
  ) => {
    if (!fieldValue) return;

    if (!/^\d+$/.test(value)) return;

    let num = Number(value);

    if (part === "hours") num = Math.min(23, Math.max(0, num));
    if (part === "minutes") num = Math.min(59, Math.max(0, num));

    const date = new Date(fieldValue);
    if (isNaN(date.getTime())) return;

    if (part === "hours") date.setHours(num);
    if (part === "minutes") date.setMinutes(num);

    onChange(date.toString());
  };

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => {
        const date = field.value ? new Date(field.value) : null;
        const hours = date ? String(date.getHours()).padStart(2, "0") : "";
        const minutes = date ? String(date.getMinutes()).padStart(2, "0") : "";

        return editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <div className="flex items-center gap-2">
                <Input
                  value={hours}
                  type="text"
                  inputMode="numeric"
                  pattern="^(?:[0-9]|1[0-9]|2[0-3])$"
                  placeholder="HH"
                  className="w-10 shadow-none"
                  onChange={(e) =>
                    handleTimeChange(
                      field.onChange,
                      field.value,
                      "hours",
                      e.target.value,
                    )
                  }
                />
                <span className="font-bold">:</span>
                <Input
                  value={minutes}
                  type="text"
                  inputMode="numeric"
                  pattern="^(?:[0-9]|[1-5][0-9])$"
                  placeholder="MM"
                  className="w-10 shadow-none"
                  onChange={(e) =>
                    handleTimeChange(
                      field.onChange,
                      field.value,
                      "minutes",
                      e.target.value,
                    )
                  }
                />
              </div>
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
              {field.value ? formatTime(field.value) : "N/A"}
            </p>
          </FormItem>
        );
      }}
    />
  );
}
