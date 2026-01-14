import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import profileSchema, {
  AddProfileFormData,
} from "@/features/admin/schemas/profileSchema";
import useAddProfile from "@/features/admin/hooks/useAddProfile";

export default function AddProfile({ userId }: { userId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const mutation = useAddProfile(userId);

  const form = useForm<AddProfileFormData>({
    resolver: zodResolver(profileSchema.addProfile),
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

  const onSubmit = (data: AddProfileFormData) => {
    mutation.mutate(data, {
      onSuccess: () => {
        form.reset();
        setIsOpen(false);
      },
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <DropdownMenuItem
          onSelect={(e) => e.preventDefault()}
          onClick={() => setIsOpen(true)}
          className="font-receipt font-semibold"
        >
          <UserPlus />
          Kreiraj profil
        </DropdownMenuItem>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md font-receipt overflow-y-auto max-h-[calc(100dvh-2rem)] h-fit">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Kreiraj korisnika</DialogTitle>
              <DialogDescription>
                Ispunite obrazac ispod da biste kreirali profil korisnika u
                sistem.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Ime <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Ime"
                        type="text"
                        {...field}
                        required
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Prezime <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Prezime"
                        type="text"
                        {...field}
                        required
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="country"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Država </FormLabel>
                    <FormControl>
                      <Input placeholder="Država" type="text" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Grad </FormLabel>
                    <FormControl>
                      <Input placeholder="Grad" type="text" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Adresa </FormLabel>
                    <FormControl>
                      <Input placeholder="Adresa" type="text" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="phone_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Broj telefona </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Broj telefona"
                        type="text"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="date_of_birth"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Datum rođenja </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Datum rođenja"
                        type="date"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="currency_preference"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Novčana valuta</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Novčana valuta"
                        type="text"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <DialogClose asChild>
                <Button
                  variant="outline"
                  disabled={mutation.isPending}
                  className="font-semibold"
                >
                  Odustani
                </Button>
              </DialogClose>
              <LoadingButton
                type="submit"
                loading={mutation.isPending}
                className="font-semibold"
              >
                Spremi
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
