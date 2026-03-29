"use client";

import { useCallback, useEffect, useState } from "react";
import type { Chore, CreateChoreRequest, UpdateChoreRequest } from "@/types/chore";
import * as choreApi from "@/lib/api/chores";

/**
 * Manage chore state with CRUD operations.
 * @returns Chore list, loading state, and mutation functions.
 */
export function useChores() {
  const [chores, setChores] = useState<Chore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChores = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await choreApi.listChores();
      setChores(data);
    } catch {
      setError("Failed to load chores");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChores();
  }, [fetchChores]);

  const createChore = useCallback(
    async (data: CreateChoreRequest) => {
      const newChore = await choreApi.createChore(data);
      setChores((prev) => [...prev, newChore]);
      return newChore;
    },
    [],
  );

  const updateChore = useCallback(
    async (id: string, data: UpdateChoreRequest) => {
      const updated = await choreApi.updateChore(id, data);
      setChores((prev) => prev.map((c) => (c.id === id ? updated : c)));
      return updated;
    },
    [],
  );

  const deleteChore = useCallback(
    async (id: string) => {
      await choreApi.deleteChore(id);
      setChores((prev) => prev.filter((c) => c.id !== id));
    },
    [],
  );

  return {
    chores,
    isLoading,
    error,
    fetchChores,
    createChore,
    updateChore,
    deleteChore,
  };
}
