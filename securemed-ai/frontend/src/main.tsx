import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./hooks/useAuth";
import { PresentationProvider } from "./hooks/usePresentationMode";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PresentationProvider>
          <App />
        </PresentationProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
