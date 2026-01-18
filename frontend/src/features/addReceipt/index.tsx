import { ReceiptCard } from "@/components/Common/ReceiptCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import OCREntry from "./components/OCREntry";
import { ManualEntry } from "./components/ManualEntry";

const tabsConfig = [
  { value: "manual", title: "Unos Računa", component: ManualEntry },
  { value: "ocr", title: "OCR Učitavanje", component: OCREntry },
];

export default function AddReceipt() {
  return (
    <section>
      <ReceiptCard className="h-full">
        <div className="flex flex-col min-h-full gap-6 bg-card p-4 lg:p-8">
          <div className="self-start">
            <h1 className="text-4xl font-bold tracking-tight">Dodaj Račun</h1>
            <p className="text-muted-foreground">
              Unesi te svoj današnji trošak
            </p>
          </div>
          <Tabs defaultValue="manual">
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
    </section>
  );
}
