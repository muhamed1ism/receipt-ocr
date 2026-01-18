import DynamicFormField from "@/components/Forms/DynamicFormField";
import { currencyPreference } from "@/constants/currency-preference";
import { AddReceiptFormData } from "@/features/addReceipt/schemas/receiptsShema";
import { UseFormReturn } from "react-hook-form";

interface TotalPriceProps {
  form: UseFormReturn<AddReceiptFormData>;
}

export default function TotalPrice({ form }: TotalPriceProps) {
  const currencyValue = form.watch("currency"); // reactive
  const currency =
    currencyPreference.find((c) => c.value === currencyValue) ||
    currencyPreference[0];

  return (
    <>
      <h2 className="text-xl font-bold">Ukupno</h2>
      <div className="grid grid-cols-2 gap-4 lg:gap-8">
        <DynamicFormField
          control={form.control}
          name="tax_amount"
          label="Porez"
          type="decimal"
          append={currency.position === "append" ? currency.symbol : undefined}
          prepend={
            currency.position === "prepend" ? currency.symbol : undefined
          }
          disabled
        />
        <DynamicFormField
          control={form.control}
          name="total_amount"
          label="Ukupan iznos"
          type="decimal"
          append={currency.position === "append" ? currency.symbol : undefined}
          prepend={
            currency.position === "prepend" ? currency.symbol : undefined
          }
          disabled
        />
      </div>
    </>
  );
}
