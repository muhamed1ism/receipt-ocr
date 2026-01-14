import { ReceiptCard } from "@/components/Common/ReceiptCard";
import { Button } from "@/components/ui/button";
import { LoadingButton } from "@/components/ui/loading-button";
import { useForm } from "react-hook-form";
import useAddProfileMe from "./hooks/useAddProfileMe";
import profileSchema, { AddProfileMeFormData } from "./schemas/profileSchema";
import { zodResolver } from "@hookform/resolvers/zod";
import DynamicFormField from "@/components/Forms/DynamicFormField";
import { currencyPreference } from "@/constants/currency-preference";
import { Form } from "@/components/ui/form";

export default function PostRegister() {
  const mutation = useAddProfileMe();

  const form = useForm<AddProfileMeFormData>({
    resolver: zodResolver(profileSchema.addProfileMe),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      first_name: "",
      last_name: "",
      phone_number: "",
      date_of_birth: "",
      country: "",
      address: "",
      city: "",
      currency_preference: "BAM",
    },
  });

  const onSubmit = (data: AddProfileMeFormData) => {
    mutation.mutate(data);
  };

  return (
    <section className="flex justify-center items-center h-full w-full mt-[calc(100dvh/10)]">
      <ReceiptCard>
        <Form {...form}>
          <form
            className="bg-card p-6 sm:max-w-xl font-receipt overflow-y-auto max-h-[calc(100dvh-2rem)] h-fit"
            onSubmit={form.handleSubmit(onSubmit)}
          >
            <h1 className="text-3xl font-bold">Kreiraj profil</h1>
            <p>Ispunite obrazac ispod da biste kreirali svoj profil.</p>
            <div className="grid grid-cols-2 gap-8 py-8">
              <DynamicFormField
                name="first_name"
                type="text"
                control={form.control}
                label="Ime"
              />

              <DynamicFormField
                name="last_name"
                type="text"
                control={form.control}
                label="Prezime"
              />

              <DynamicFormField
                name="country"
                type="text"
                control={form.control}
                label="Država"
              />

              <DynamicFormField
                name="city"
                type="text"
                control={form.control}
                label="Grad"
              />

              <DynamicFormField
                name="address"
                type="text"
                control={form.control}
                label="Adresa"
              />

              <DynamicFormField
                name="phone_number"
                type="text"
                control={form.control}
                label="Broj telefona"
              />

              <DynamicFormField
                name="date_of_birth"
                type="date"
                control={form.control}
                label="Datum rođenja"
              />

              <DynamicFormField
                name="currency_preference"
                type="select"
                control={form.control}
                label="Novčana valuta"
                options={currencyPreference}
              />
            </div>

            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                disabled={mutation.isPending}
                className="font-semibold"
              >
                Odustani
              </Button>
              <LoadingButton
                type="submit"
                loading={mutation.isPending}
                className="font-semibold"
              >
                Spremi
              </LoadingButton>
            </div>
          </form>
        </Form>
      </ReceiptCard>
    </section>
  );
}
