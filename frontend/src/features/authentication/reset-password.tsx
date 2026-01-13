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
import { LoadingButton } from "@/components/ui/loading-button";
import { PasswordInput } from "@/components/ui/password-input";
import { Route } from "@/routes/reset-password";
import authSchema, { ResetPasswordFormData } from "./schemas/authSchema";
import useResetPassword from "./hooks/useResetPassword";

export default function ResetPassword() {
  const { token } = Route.useSearch();
  const mutation = useResetPassword();

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(authSchema.resetPassword),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  const onSubmit = (data: ResetPasswordFormData) => {
    mutation.mutate(
      { new_password: data.new_password, token },
      {
        onSuccess: () => {
          form.reset();
        },
      },
    );
  };

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Reset Password</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="new-password-input"
                      placeholder="New Password"
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
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="confirm-password-input"
                      placeholder="Confirm Password"
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
              Reset Password
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Remember your password?{" "}
            <RouterLink to="/login" className="underline underline-offset-4">
              Log in
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
}
