"use client";

import { useCallback, useEffect, useState } from "react";
import type { BucketItem, BucketDraw, CreateBucketItemRequest, UpdateBucketItemRequest } from "@/types/bucket";
import * as bucketApi from "@/lib/api/bucket";

/**
 * Manage bucket items and draw state.
 * @returns Bucket items, active draw, and mutation functions.
 */
export function useBucket() {
  const [items, setItems] = useState<BucketItem[]>([]);
  const [activeDraw, setActiveDraw] = useState<BucketDraw | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchItems = useCallback(async () => {
    try {
      const data = await bucketApi.listItems();
      setItems(data);
    } catch {
      /* ignore */
    }
  }, []);

  const fetchActiveDraw = useCallback(async () => {
    try {
      const data = await bucketApi.getActiveDraw();
      setActiveDraw(data);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([fetchItems(), fetchActiveDraw()]).finally(() => setIsLoading(false));
  }, [fetchItems, fetchActiveDraw]);

  const createItem = useCallback(async (data: CreateBucketItemRequest) => {
    const newItem = await bucketApi.createItem(data);
    setItems((prev) => [...prev, newItem]);
    return newItem;
  }, []);

  const updateItem = useCallback(async (id: string, data: UpdateBucketItemRequest) => {
    const updated = await bucketApi.updateItem(id, data);
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
    return updated;
  }, []);

  const deleteItem = useCallback(async (id: string) => {
    await bucketApi.deleteItem(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const draw = useCallback(async () => {
    const newDraw = await bucketApi.draw();
    setActiveDraw(newDraw);
    return newDraw;
  }, []);

  const resolveDraw = useCallback(async (drawId: string) => {
    const resolved = await bucketApi.resolveDraw(drawId);
    setActiveDraw(null);
    return resolved;
  }, []);

  const returnDraw = useCallback(async (drawId: string, justification: string) => {
    const returned = await bucketApi.returnDraw(drawId, justification);
    setActiveDraw(null);
    return returned;
  }, []);

  return {
    items,
    activeDraw,
    isLoading,
    fetchItems,
    fetchActiveDraw,
    createItem,
    updateItem,
    deleteItem,
    draw,
    resolveDraw,
    returnDraw,
  };
}
