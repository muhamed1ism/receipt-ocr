import Receipts from "@/components/Admin/Receipts";
import Users from "@/components/Admin/Users";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ReceiptCard } from "@/components/Common/ReceiptCard";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
});

const tabsConfig = [
  { value: "users", title: "Korisnici", component: Users },
  { value: "receipts", title: "Računi", component: Receipts },
];

function Admin() {
  return (
    <ReceiptCard>
      <div className="flex flex-col min-h-[540px] md:min-h-full gap-6 bg-card p-4 lg:p-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Admin</h1>
          <p className="text-muted-foreground">
            Upravljanje sistemom, korisničkim računima i administrativnim
            postavkama{" "}
          </p>{" "}
        </div>
        <Tabs defaultValue="users">
          <TabsList className="bg-background">
            {tabsConfig.map((tab) => (
              <TabsTrigger
                className="font-semibold data-[state=active]:bg-card"
                key={tab.value}
                value={tab.value}
              >
                {tab.title}
              </TabsTrigger>
            ))}
          </TabsList>
          {tabsConfig.map((tab) => (
            <TabsContent key={tab.value} value={tab.value} className="mt-4">
              <tab.component />
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </ReceiptCard>
  );
}
