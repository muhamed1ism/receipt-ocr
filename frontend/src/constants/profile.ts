const PROFILE_FIELDS: {
  name: keyof FormData;
  label: string;
  type: "text" | "date" | "select";
}[] = [
  { name: "first_name", label: "Ime", type: "text" },
  { name: "last_name", label: "Prezime", type: "text" },
  { name: "country", label: "Država", type: "text" },
  { name: "city", label: "Grad", type: "text" },
  { name: "address", label: "Adresa", type: "text" },
  { name: "phone_number", label: "Broj telefona", type: "text" },
  { name: "date_of_birth", label: "Datum rođenja", type: "date" },
  { name: "currency_preference", label: "Novčana valuta", type: "select" },
];
