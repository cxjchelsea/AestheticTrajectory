import { createContext, useContext } from "react";

export type SessionContextValue = {
  userId: string;
  authMode: string;
  sessionReady: boolean;
};

export const SessionContext = createContext<SessionContextValue>({
  userId: "user_anonymous",
  authMode: "dev",
  sessionReady: false
});

export function useSession() {
  return useContext(SessionContext);
}
