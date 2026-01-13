import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { LoadingButton } from "@/components/ui/loading-button";
import { PasswordInput } from "@/components/ui/password-input";
import settingsSchema, {
  ChangePasswordFormData,
} from "../../schemas/settingsSchema";
import useChangePassword from "@/features/receipts/hooks/useChangePassword";

const ChangePassword = () => {
  const mutation = useChangePassword();

  const form = useForm<ChangePasswordFormData>({
    resolver: zodResolver(settingsSchema.changePassword),
    mode: "onSubmit",
    criteriaMode: "all",
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  const onSubmit = async (data: ChangePasswordFormData) => {
    mutation.mutate(data, {
      onSuccess: () => {
        form.reset();
      },
    });
  };

  return (
    <div className="max-w-md">
      <h3 className="text-xl font-semibold py-4">Promijeni lozinku</h3>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
        >
          <FormField
            control={form.control}
            name="current_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Trenutna lozinka</FormLabel>
                <FormControl>
                  <PasswordInput
                    data-testid="current-password-input"
                    placeholder="••••••••"
                    aria-invalid={fieldState.invalid}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="new_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Nova lozinka</FormLabel>
                <FormControl>
                  <PasswordInput
                    data-testid="new-password-input"
                    placeholder="••••••••"
                    aria-invalid={fieldState.invalid}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirm_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Potvrdi novu lozinku</FormLabel>
                <FormControl>
                  <PasswordInput
                    className="font-sans font-normal"
                    data-testid="confirm-password-input"
                    placeholder="••••••••"
                    aria-invalid={fieldState.invalid}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <LoadingButton
            type="submit"
            loading={mutation.isPending}
            className="self-start font-semibold"
          >
            Ažuriraj lozinku
          </LoadingButton>
        </form>
      </Form>
    </div>
  );
};

export default ChangePassword;
