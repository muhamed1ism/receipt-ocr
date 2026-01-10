import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ProfileService, ProfileUpdate } from "@/client";
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
import useCustomToast from "@/hooks/useCustomToast";
import { cn } from "@/lib/utils";
import { handleError } from "@/utils";
import useAuth from "@/hooks/useAuth";

const formSchema = z.object({
  first_name: z.string().max(30),
  last_name: z.string().max(30),
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
    const updateData: ProfileUpdate = {};

    if (data.first_name !== currentUser?.profile?.first_name) {
      updateData.first_name = data.first_name;
    }
    if (data.last_name !== currentUser?.profile?.last_name) {
      updateData.last_name = data.last_name;
    }

    if (!Object.keys(updateData).length) {
      toggleEditMode();
      return;
    }

    mutation.mutate(updateData);
  };

  useEffect(() => {
    if (!currentUser) return;

    form.reset({
      first_name: currentUser.profile?.first_name ?? "",
      last_name: currentUser.profile?.last_name ?? "",
    });
  }, [currentUser]);

  const onCancel = () => {
    form.reset({
      first_name: currentUser?.profile?.first_name,
      last_name: currentUser?.profile?.last_name,
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
