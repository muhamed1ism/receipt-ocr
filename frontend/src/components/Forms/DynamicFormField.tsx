import { Control, FieldValues, Path } from "react-hook-form";
import TextFormField from "./TextFormField";
import DateFormField from "./DateFormField";
import SelectFormField, { OptionType } from "./SelectFormField";
import TimeFormField from "./TimeFormField";

interface DynamicFormFieldProps<T extends FieldValues> {
  name: Path<T>;
  type: "text" | "date" | "time" | "select";
  control: Control<T>;
  label: string;
  editMode?: boolean | string;
  options?: OptionType[];
}

export default function DynamicFormField<T extends FieldValues>({
  name,
  type,
  control,
  label,
  editMode = "disabled",
  options,
}: DynamicFormFieldProps<T>) {
  return (
    <>
      {type === "text" ? (
        <TextFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
        />
      ) : type === "date" ? (
        <DateFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
        />
      ) : type === "time" ? (
        <TimeFormField
          name={name}
          control={control}
          label={label}
          editMode={editMode}
        />
      ) : (
        type === "select" &&
        options && (
          <SelectFormField
            name={name}
            control={control}
            label={label}
            editMode={editMode}
            options={options}
          />
        )
      )}
    </>
  );
}
