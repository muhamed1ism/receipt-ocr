import { createFileRoute } from "@tanstack/react-router";

import ChangePassword from "@/components/UserSettings/ChangePassword";
import DeleteAccount from "@/components/UserSettings/DeleteAccount";
import ChangeEmail from "@/components/UserSettings/ChangeEmail";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import useAuth from "@/hooks/useAuth";
import ProfileInformation from "@/components/UserSettings/ProfileInformation";
import { ReceiptCard } from "@/components/Common/ReceiptCard";

const tabsConfig = [
  { value: "my-profile", title: "Moj Profil", component: ProfileInformation },
  { value: "email", title: "Email", component: ChangeEmail },
  { value: "password", title: "Lozinka", component: ChangePassword },
  {
    value: "danger-zone",
    title: "Obriši račun",
    component: DeleteAccount,
  },
];

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
});

function UserSettings() {
  const { user: currentUser } = useAuth();
  const finalTabs = currentUser?.is_superuser
    ? tabsConfig.slice(0, 4)
    : tabsConfig;

  if (!currentUser) {
    return null;
  }

  return (
    <ReceiptCard>
      <div className="flex flex-col min-h-[540px] md:min-h-full gap-6 bg-card p-4 lg:p-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Postavke korisnika
          </h1>
          <p className="text-muted-foreground">
            Upravljajte postavkama i preferencijama svog računa{" "}
          </p>
        </div>

        <Tabs defaultValue="my-profile">
          <TabsList className="flex flex-wrap bg-background">
            {finalTabs.map((tab) => (
              <TabsTrigger
                className="font-semibold data-[state=active]:bg-card"
                key={tab.value}
                value={tab.value}
              >
                {tab.title}
              </TabsTrigger>
            ))}
          </TabsList>
          {finalTabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value}>
              <tab.component />
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </ReceiptCard>
  );
}
