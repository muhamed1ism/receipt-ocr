import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { UsersService, type UserUpdateMe } from "@/client";
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
import { handleError } from "@/utils";

const formSchema = z.object({
  email: z.email({ message: "Nevažeća email adresa" }),
});

type FormData = z.infer<typeof formSchema>;

const ChangeEmail = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const [editMode, setEditMode] = useState(false);
  const { user: currentUser } = useAuth();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: currentUser?.email,
    },
  });

  const toggleEditMode = () => {
    setEditMode(!editMode);
  };

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Korisnik je uspješno ažuriran");
      toggleEditMode();
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries();
    },
  });

  const onSubmit = (data: FormData) => {
    const emailChanged = data.email !== currentUser?.email;

    if (!emailChanged) {
      toggleEditMode();
      return;
    }

    mutation.mutate({ email: data.email });
  };

  useEffect(() => {
    if (currentUser?.email) {
      form.reset({ email: currentUser.email });
    }
  }, [currentUser?.email]);

  const onCancel = () => {
    form.reset({ email: currentUser?.email });
    toggleEditMode();
  };

  return (
    <div className="max-w-md">
      <h3 className="text-xl font-bold py-4">Promijeni e-mail adresu</h3>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
        >
          <FormField
            control={form.control}
            name="email"
            render={({ field }) =>
              editMode ? (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      className="font-normal font-sans"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              ) : (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <p className="py-2 truncate max-w-sm font-normal font-sans">
                    {field.value}
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

export default ChangeEmail;
