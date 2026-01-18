import { Control, FieldValues, Path } from "react-hook-form";
import TextFormField from "./TextFormField";
import DateFormField from "./DateFormField";
import SelectFormField, { OptionType } from "./SelectFormField";
import NumberFormField from "./NumberFormField";
import TimeFormField from "./TimeFormField";
import DecimalFormField from "./DecimalFormField";

interface DynamicFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  type: "text" | "date" | "time" | "select" | "number" | "decimal";
  control: Control<T>;
  label: string;
  inputClassName?: string;
  className?: string;
  editMode?: boolean | string;
  options?: OptionType[];
  disabled?: boolean;
  onChange?: (value: number | undefined) => void;
  prepend?: string;
  append?: string;
}

export default function DynamicFormField<T extends FieldValues>({
  name,
  type,
  control,
  label,
  inputClassName,
  className,
  editMode = "disabled",
  options,
  disabled,
  onChange,
  prepend,
  append,
}: DynamicFormFieldProps<T>) {
  return (
    <div className="w-full h-full">
      {type === "text" ? (
        <TextFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          inputClassName={inputClassName}
          className={className}
        />
      ) : type === "date" ? (
        <DateFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          inputClassName={inputClassName}
          className={className}
        />
      ) : type === "time" ? (
        <TimeFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          inputClassName={inputClassName}
          className={className}
        />
      ) : type === "select" && options ? (
        <SelectFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          options={options}
          inputClassName={inputClassName}
          className={className}
        />
      ) : type === "number" ? (
        <NumberFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          disabled={disabled}
          onChange={onChange}
          inputClassName={inputClassName}
          className={className}
          prepend={prepend}
          append={append}
        />
      ) : type === "decimal" ? (
        <DecimalFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
          disabled={disabled}
          onChange={onChange}
          inputClassName={inputClassName}
          className={className}
          prepend={prepend}
          append={append}
        />
      ) : null}
    </div>
  );
}
