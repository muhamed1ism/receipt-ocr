import type React from "react";
import { ReceiptCard } from "@/components/Common/ReceiptCard";

export const OCREntry: React.FC = () => {
  return (
    <div>
      <ReceiptCard className="flex flex-col md:min-h-full gap-6 bg-card p-4 lg:p-8">
        <h2>OCR Funkcionalnost</h2>
        <p>OCR funkcionalnost će biti dostupna uskoro</p>
      </ReceiptCard>
    </div>
  );
};

export default OCREntry;
