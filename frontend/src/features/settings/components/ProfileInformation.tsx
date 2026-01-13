import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Suspense, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ProfileService, type ProfileUpdate } from "@/client";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { LoadingButton } from "@/components/ui/loading-button";
import useAuth from "@/hooks/useAuth";
import useCustomToast from "@/hooks/useCustomToast";
import { cn } from "@/lib/utils";
import { handleError } from "@/utils";
import PendingSettingsProfile from "../Pending/PendingSettingsProfile";
import { formatDate } from "@/utils/formatDateTime";
import { DatePicker } from "../ui/date-picker";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
} from "../ui/select";
import { SelectValue } from "@radix-ui/react-select";
import { currencyPreference } from "@/constants/currency-preference";

const formSchema = z.object({
  first_name: z.string().max(30),
  last_name: z.string().max(30),
  phone_number: z.string().max(30).optional(),
  date_of_birth: z.date().optional(),
  country: z.string().max(30).optional(),
  address: z.string().max(30).optional(),
  city: z.string().max(30).optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
});

type FormData = z.infer<typeof formSchema>;

const ProfileInformation = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const [editMode, setEditMode] = useState(false);
  const { user: currentUser } = useAuth();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
      phone_number: currentUser?.profile?.phone_number || "",
      date_of_birth: new Date(currentUser?.profile?.date_of_birth || ""),
      country: currentUser?.profile?.country || "",
      address: currentUser?.profile?.address || "",
      city: currentUser?.profile?.city || "",
      currency_preference: currentUser?.profile?.currency_preference,
    },
  });

  const toggleEditMode = () => {
    setEditMode(!editMode);
  };

  const mutation = useMutation({
    mutationFn: (data: ProfileUpdate) =>
      ProfileService.updateProfileMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Profil je uspješno ažuriran");
      toggleEditMode();
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries();
    },
  });

  const onSubmit = (data: FormData) => {
    const updateData: Partial<ProfileUpdate> = {};

    (Object.keys(data) as (keyof FormData)[]).forEach((key) => {
      if (data[key] !== currentUser?.profile?.[key]) {
        if (data[key] instanceof Date) {
          updateData[key] = data[key].toLocaleDateString("en-CA");
        } else {
          updateData[key] = data[key];
        }
      }
    });

    if (!Object.keys(updateData).length) {
      toggleEditMode();
      return;
    }

    console.log(updateData);

    mutation.mutate(updateData);
  };

  useEffect(() => {
    if (!currentUser) return;

    form.reset({
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
      phone_number: currentUser?.profile?.phone_number || "",
      date_of_birth: new Date(currentUser?.profile?.date_of_birth || ""),
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
      date_of_birth: new Date(currentUser?.profile?.date_of_birth || ""),
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
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Ime</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          className="font-normal font-sans"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Ime</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Prezime</FormLabel>
                      <FormControl>
                        <Input type="text font-normal font-sans" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Prezime</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="country"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Država</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          className="font-normal font-sans"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Država</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="city"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Grad</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          className="font-normal font-sans"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Grad</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="address"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Adresa</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          className="font-normal font-sans"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Adresa</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="phone_number"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Broj telefona</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          className="font-normal font-sans"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Broj telefona</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="date_of_birth"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Datum rođenja</FormLabel>
                      <FormControl>
                        <DatePicker
                          date={field.value}
                          setDate={field.onChange}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Datum rođenja</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value ? formatDate(field.value) : "N/A"}
                      </p>
                    </FormItem>
                  )
                }
              />

              <FormField
                control={form.control}
                name="currency_preference"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Novčana valuta</FormLabel>
                      <FormControl>
                        <Select {...field} onValueChange={field.onChange}>
                          <SelectTrigger className="flex font-sans border-0 border-b-2 border-dashed border-foreground/50 bg-transparent dark:bg-accent rounded-none shadow-none data-[state=open]:border-foreground">
                            <SelectValue placeholder="odaberi valutu" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectGroup>
                              {currencyPreference.map((currency, index) => (
                                <SelectItem key={index} value={currency.value}>
                                  {currency.label}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel>Novčana valuta</FormLabel>
                      <p
                        className={cn(
                          "py-2 truncate max-w-sm font-normal font-sans",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        {field.value || "N/A"}
                      </p>
                    </FormItem>
                  )
                }
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
