"use client";

import { useContext } from "react";
import { AuthContext } from "@/lib/contexts/auth-context";

/**
 * Access the authentication context.
 * @returns Authentication state and methods (user, login, register, logout).
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
