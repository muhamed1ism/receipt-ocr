import DynamicFormField from "@/components/Forms/DynamicFormField";
import { AddReceiptFormData } from "@/features/addReceipt/schemas/receiptsShema";
import { ChevronRight } from "lucide-react";
import { useState } from "react";
import { UseFormReturn } from "react-hook-form";

interface StoreInfoProps {
  form: UseFormReturn<AddReceiptFormData>;
}

export default function StoreInfo({ form }: StoreInfoProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="space-y-4 mt-2">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xl font-bold hover:text-muted-foreground"
      >
        <ChevronRight
          size={18}
          className={`transition-transform ${expanded ? "rotate-90" : ""}`}
        />
        Podaci o prodavnici
      </button>
      {expanded && (
        <div className="grid lg:grid-cols-2 gap-4 lg:gap-8">
          <DynamicFormField
            label="Naziv prodavnice"
            control={form.control}
            name="store.name"
            type="text"
          />
          <DynamicFormField
            label="Grad"
            control={form.control}
            name="branch.city"
            type="text"
          />
          <DynamicFormField
            label="Adresa"
            control={form.control}
            name="branch.address"
            type="text"
          />

          <div className="flex w-full lg:justify-evenly gap-4">
            <DynamicFormField
              control={form.control}
              name="date_time"
              label="Datum"
              inputClassName=""
              type="date"
            />
            <div className="w-full flex justify-around">
              <DynamicFormField
                control={form.control}
                name="date_time"
                inputClassName="w-full"
                label="Vrijeme"
                type="time"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
