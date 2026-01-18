import DynamicFormField from "@/components/Forms/DynamicFormField";
import { currencyPreference } from "@/constants/currency-preference";
import { paymentMethod } from "@/constants/payment-method";
import { AddReceiptFormData } from "@/features/addReceipt/schemas/receiptsShema";
import { UseFormReturn } from "react-hook-form";

interface PaymentPreferenceProps {
  form: UseFormReturn<AddReceiptFormData>;
}

export default function PaymentPreference({ form }: PaymentPreferenceProps) {
  return (
    <div className="flex items-center gap-4 lg:gap-8">
      <DynamicFormField
        control={form.control}
        name="payment_method"
        label="Način plaćanja"
        inputClassName="w-full"
        type="select"
        options={paymentMethod}
      />

      <div className="flex w-full justify-around lg:justify-start">
        <DynamicFormField
          label="Valuta"
          control={form.control}
          name="currency"
          inputClassName="w-full"
          type="select"
          options={currencyPreference}
        />
      </div>
    </div>
  );
}
