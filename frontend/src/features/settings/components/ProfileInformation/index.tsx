import { zodResolver } from "@hookform/resolvers/zod";
import { Suspense, useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { type ProfileUpdate } from "@/client";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { LoadingButton } from "@/components/ui/loading-button";
import useAuth from "@/hooks/useAuth";
import PendingSettingsProfile from "./PendingSettingsProfile";
import { currencyPreference } from "@/constants/currency-preference";
import settingsSchema, {
  UpdateProfileFormData,
} from "../../schemas/settingsSchema";
import useUpdateProfile from "@/features/receipts/hooks/useUpdateProfile";
import DynamicFormField from "@/components/Forms/DynamicFormField";

const ProfileInformation = () => {
  const [editMode, setEditMode] = useState(false);
  const { user: currentUser } = useAuth();
  const mutation = useUpdateProfile();

  const form = useForm<UpdateProfileFormData>({
    resolver: zodResolver(settingsSchema.updateProfile),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
      phone_number: currentUser?.profile?.phone_number || "",
      date_of_birth: currentUser?.profile?.date_of_birth || "",
      country: currentUser?.profile?.country || "",
      address: currentUser?.profile?.address || "",
      city: currentUser?.profile?.city || "",
      currency_preference: currentUser?.profile?.currency_preference,
    },
  });

  const toggleEditMode = () => {
    setEditMode(!editMode);
  };

  const onSubmit = (data: UpdateProfileFormData) => {
    const updateData = (
      Object.keys(data) as (keyof UpdateProfileFormData)[]
    ).reduce((acc, key) => {
      if (data[key] !== currentUser?.profile?.[key]) {
        acc[key] = data[key];
      }
      return acc;
    }, {} as Partial<ProfileUpdate>);

    if (Object.keys(updateData).length === 0) {
      toggleEditMode();
      return;
    }

    mutation.mutate(updateData, { onSuccess: toggleEditMode });
  };

  useEffect(() => {
    if (!currentUser) return;

    form.reset({
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
      phone_number: currentUser?.profile?.phone_number || "",
      date_of_birth: currentUser?.profile?.date_of_birth || "",
      country: currentUser?.profile?.country || "",
      address: currentUser?.profile?.address || "",
      city: currentUser?.profile?.city || "",
      currency_preference: currentUser?.profile?.currency_preference,
    });
  }, [currentUser, form.reset]);

  const onCancel = () => {
    form.reset({
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
      phone_number: currentUser?.profile?.phone_number || "",
      date_of_birth: currentUser?.profile?.date_of_birth || "",
      country: currentUser?.profile?.country || "",
      address: currentUser?.profile?.address || "",
      city: currentUser?.profile?.city || "",
      currency_preference: currentUser?.profile?.currency_preference,
    });
    toggleEditMode();
  };

  return (
    <div className="max-w-md">
      <h3 className="text-xl font-bold py-4">
        Informacije o korisničkom profilu
      </h3>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
        >
          <Suspense fallback={<PendingSettingsProfile />}>
            <div className="grid grid-cols-2 gap-8">
              <DynamicFormField
                name="first_name"
                type="text"
                control={form.control}
                label="Ime"
                editMode={editMode}
              />

              <DynamicFormField
                name="last_name"
                type="text"
                control={form.control}
                label="Prezime"
                editMode={editMode}
              />

              <DynamicFormField
                name="country"
                type="text"
                control={form.control}
                label="Država"
                editMode={editMode}
              />

              <DynamicFormField
                name="city"
                type="text"
                control={form.control}
                label="Grad"
                editMode={editMode}
              />

              <DynamicFormField
                name="address"
                type="text"
                control={form.control}
                label="Adresa"
                editMode={editMode}
              />

              <DynamicFormField
                name="phone_number"
                type="text"
                control={form.control}
                label="Broj telefona"
                editMode={editMode}
              />

              <DynamicFormField
                name="date_of_birth"
                type="date"
                control={form.control}
                label="Datum rođenja"
                editMode={editMode}
              />

              <DynamicFormField
                name="currency_preference"
                type="select"
                control={form.control}
                label="Novčana valuta"
                editMode={editMode}
                options={currencyPreference}
              />
            </div>
          </Suspense>

          <div className="flex gap-3">
            {editMode ? (
              <>
                <LoadingButton
                  type="submit"
                  loading={mutation.isPending}
                  disabled={!form.formState.isDirty}
                  className="font-semibold"
                >
                  Spremi
                </LoadingButton>
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  disabled={mutation.isPending}
                  className="font-semibold"
                >
                  Odustani
                </Button>
              </>
            ) : (
              <Button
                type="button"
                onClick={toggleEditMode}
                className="font-semibold"
              >
                Uredi
              </Button>
            )}
          </div>
        </form>
      </Form>
    </div>
  );
};

export default ProfileInformation;
