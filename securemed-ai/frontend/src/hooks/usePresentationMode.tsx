import { createContext, useContext, useState, ReactNode } from "react";

interface PresentationContextValue {
  presentationMode: boolean;
  togglePresentationMode: () => void;
}

const PresentationContext = createContext<PresentationContextValue | undefined>(undefined);

export function PresentationProvider({ children }: { children: ReactNode }) {
  const [presentationMode, setPresentationMode] = useState(false);
  return (
    <PresentationContext.Provider
      value={{ presentationMode, togglePresentationMode: () => setPresentationMode((v) => !v) }}
    >
      {children}
    </PresentationContext.Provider>
  );
}

export function usePresentationMode(): PresentationContextValue {
  const ctx = useContext(PresentationContext);
  if (!ctx) throw new Error("usePresentationMode must be used within PresentationProvider");
  return ctx;
}
