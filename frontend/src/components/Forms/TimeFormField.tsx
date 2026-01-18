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
import { useEffect, useState } from "react";

interface TimeFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  editMode?: boolean | string;
  inputClassName?: string;
  className?: string;
}

export default function TimeFormField<T extends FieldValues>({
  name,
  control,
  label,
  inputClassName,
  className,
  editMode = "disabled",
}: TimeFormFieldProps<T>) {
  const formValue = control._formValues[name];

  const [hours, setHours] = useState("");
  const [minutes, setMinutes] = useState("");

  useEffect(() => {
    if (!formValue) return;

    const date = new Date(formValue);
    setHours(String(date.getHours()).padStart(2, "0"));
    setMinutes(String(date.getMinutes()).padStart(2, "0"));
  }, [formValue]);

  const handleHoursInput = (
    onChange: (value: string) => void,
    value: string,
  ) => {
    if (!/^\d*$/.test(value)) return;

    setHours(value);

    if (value === "") return;

    const num = Math.min(23, Number(value));

    const date = new Date(control._formValues[name]);
    date.setHours(num);
    console.log(date);

    onChange(date.toISOString());
  };

  const handleMinutesInput = (
    onChange: (value: string) => void,
    value: string,
  ) => {
    if (!/^\d*$/.test(value)) return;

    setMinutes(value);

    if (value === "") return;

    const num = Math.min(59, Number(value));

    const date = new Date(control._formValues[name]);
    date.setMinutes(num);
    console.log(date.toISOString());

    onChange(date.toISOString());
  };

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => {
        return editMode || editMode === "disabled" ? (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <div className="flex items-center gap-2">
                <Input
                  value={hours}
                  type="text"
                  inputMode="numeric"
                  placeholder="HH"
                  className={cn("w-12 text-center shadow-none", inputClassName)}
                  onChange={(e) => {
                    handleHoursInput(field.onChange, e.target.value);
                  }}
                />
                <span className="font-bold">:</span>
                <Input
                  value={minutes}
                  type="text"
                  inputMode="numeric"
                  placeholder="MM"
                  className={cn("w-12 text-center shadow-none", inputClassName)}
                  onChange={(e) => {
                    handleMinutesInput(field.onChange, e.target.value);
                  }}
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
                className,
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
