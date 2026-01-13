import { zodResolver } from "@hookform/resolvers/zod";
import { Link as RouterLink } from "@tanstack/react-router";
import { useForm } from "react-hook-form";

import { AuthLayout } from "@/components/Common/AuthLayout";
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
import authSchema, { RecoverPasswordFormData } from "./schemas/authSchema";
import useRecoverPassword from "./hooks/useRecoverPassword";

export default function RecoverPassword() {
  const mutation = useRecoverPassword();

  const form = useForm<RecoverPasswordFormData>({
    resolver: zodResolver(authSchema.recoverPassword),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: RecoverPasswordFormData) => {
    if (mutation.isPending) return;
    mutation.mutate(data, {
      onSuccess: () => {
        form.reset();
      },
    });
  };

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Password Recovery</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold">Email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="user@example.com"
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              className="w-full"
              loading={mutation.isPending}
            >
              Continue
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Remember your password?{" "}
            <RouterLink
              to="/login"
              className="underline underline-offset-4 font-semibold"
            >
              Log in
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
}
