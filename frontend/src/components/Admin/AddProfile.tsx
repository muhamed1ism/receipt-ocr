import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { UserPlus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import z from "zod"
import { type ProfileCreate, ProfileService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Button } from "../ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { DropdownMenuItem } from "../ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form"
import { Input } from "../ui/input"
import { LoadingButton } from "../ui/loading-button"

const formSchema = z.object({
  first_name: z.string(),
  last_name: z.string(),
  phone_number: z.string().optional(),
  date_of_birth: z.string().optional(),
  country: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
})

type FormData = z.infer<typeof formSchema>

const AddProfile = ({ userId }: { userId: string }) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
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
  })

  const mutation = useMutation({
    mutationFn: (data: ProfileCreate) =>
      ProfileService.createProfile({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Profil je uspješno kreiran")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const normalizePhone = (phone?: string) => phone?.replace(/\s+/g, "").trim()

  const onSubmit = (data: FormData) => {
    mutation.mutate({
      ...data,
      phone_number: normalizePhone(data.phone_number),
      user_id: userId,
    })
  }

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
      <DialogContent className="sm:max-w-md font-receipt">
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
  )
}

export default AddProfile
