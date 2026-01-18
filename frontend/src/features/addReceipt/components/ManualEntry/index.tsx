import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import receiptsShema, { AddReceiptFormData } from "../../schemas/receiptsShema";
import useAddReceipt from "../../hooks/useAddReceipt";
import StoreInfo from "./Categories/StoreInfo";
import ReceiptDetails from "./Categories/ReceiptDetails";
import ReceiptItems from "./Categories/ReceiptItems";
import TotalPrice from "./Categories/TotalPrice";
import PaymentPreference from "./Categories/PaymentPreference";
import useAuth from "@/hooks/useAuth";

export function ManualEntry() {
  const { user } = useAuth();
  const mutation = useAddReceipt();

  const form = useForm<AddReceiptFormData>({
    resolver: zodResolver(receiptsShema.addReceipt),
    defaultValues: {
      store: { name: "", jib: "", pib: "" },
      branch: { address: "", city: "" },
      details: {
        ibfm: "",
        bf: 0,
        digital_signature: "",
      },
      date_time: new Date().toISOString(),
      payment_method: "Gotovina",
      currency: user?.profile?.currency_preference || "BAM",
      tax_amount: 0,
      total_amount: 0,
      items: [{ name: "", quantity: 0, price: 0, total_price: 0 }],
    },
  });

  const onSubmit = (data: AddReceiptFormData) => {
    mutation.mutate(data);
  };

  return (
    <div className="font-receipt flex flex-col max-w-3xl mx-auto gap-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Store Info Section */}
          <StoreInfo form={form} />

          {/* Technical Details Section (Collapsible) */}
          <ReceiptDetails form={form} />

          <div className="border-b-2 border-dashed border-muted-foreground" />

          {/* Items Section */}
          <ReceiptItems form={form} />

          <div className="border-b-2 border-dashed border-muted-foreground" />

          {/* Receipt Details Section */}
          <PaymentPreference form={form} />

          {/* Totals Section - outside ReceiptCard */}
          <TotalPrice form={form} />

          <Button type="submit" className="my-4 w-full">
            Dodaj račun
          </Button>
        </form>
      </Form>
    </div>
  );
}
