"use client";

import { useCallback, useState } from "react";
import { useTranslations } from "next-intl";
import { useBucket } from "@/lib/hooks/use-bucket";
import { ActiveDrawDisplay } from "@/components/bucket/active-draw-display";
import { BucketDrawCard } from "@/components/bucket/bucket-draw-card";
import { BucketItemForm } from "@/components/bucket/bucket-item-form";
import { ReturnJustificationModal } from "@/components/bucket/return-justification-modal";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { Sparkles, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { BucketItem, CreateBucketItemRequest } from "@/types/bucket";

/** Adult bucket page with active draw, draw button, item management, and return justification. */
export default function BucketPage() {
  const t = useTranslations("bucket");
  const tCommon = useTranslations("common");
  const {
    items,
    activeDraw,
    isLoading,
    createItem,
    updateItem,
    deleteItem,
    draw,
    resolveDraw,
    returnDraw,
  } = useBucket();

  const [formOpen, setFormOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<BucketItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<BucketItem | null>(null);
  const [showReturn, setShowReturn] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);

  const handleAdd = useCallback(() => {
    setEditingItem(null);
    setFormOpen(true);
  }, []);

  const handleEdit = useCallback((item: BucketItem) => {
    setEditingItem(item);
    setFormOpen(true);
  }, []);

  const handleSubmit = useCallback(
    async (data: CreateBucketItemRequest) => {
      try {
        if (editingItem) {
          await updateItem(editingItem.id, data);
          toast.success(t("itemUpdated"));
        } else {
          await createItem(data);
          toast.success(t("itemCreated"));
        }
        setFormOpen(false);
        setEditingItem(null);
      } catch {
        toast.error(tCommon("error"));
      }
    },
    [editingItem, createItem, updateItem, t, tCommon],
  );

  const handleDelete = useCallback(
    async (item: BucketItem) => {
      try {
        await deleteItem(item.id);
        toast.success(t("itemDeleted"));
        setDeleteTarget(null);
      } catch {
        toast.error(tCommon("error"));
      }
    },
    [deleteItem, t, tCommon],
  );

  const handleDraw = useCallback(async () => {
    setIsDrawing(true);
    try {
      await draw();
      toast.success(t("drawSuccess"));
    } catch {
      toast.error(tCommon("error"));
    } finally {
      setIsDrawing(false);
    }
  }, [draw, t, tCommon]);

  const handleResolve = useCallback(async () => {
    if (!activeDraw) return;
    setIsActionLoading(true);
    try {
      await resolveDraw(activeDraw.id);
      toast.success(t("resolveSuccess"));
    } catch {
      toast.error(tCommon("error"));
    } finally {
      setIsActionLoading(false);
    }
  }, [activeDraw, resolveDraw, t, tCommon]);

  const handleReturn = useCallback(
    async (justification: string) => {
      if (!activeDraw) return;
      await returnDraw(activeDraw.id, justification);
      toast.success(t("returnSuccess"));
    },
    [activeDraw, returnDraw, t],
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="size-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">{t("title")}</h1>
        <Button
          onClick={handleAdd}
          className="bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5"
        >
          <Plus className="size-4" />
          {t("addItem")}
        </Button>
      </div>

      <AnimatePresence mode="wait">
        {activeDraw ? (
          <motion.div
            key="active-draw"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <ActiveDrawDisplay
              draw={activeDraw}
              onResolve={handleResolve}
              onReturn={() => setShowReturn(true)}
              isLoading={isActionLoading}
            />
          </motion.div>
        ) : (
          <motion.div
            key="draw-button"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <Card className="border-dashed border-2 border-purple-300 dark:border-purple-700">
              <CardContent className="flex flex-col items-center justify-center py-10 gap-4">
                <p className="text-sm text-muted-foreground">{t("noDraw")}</p>
                <Button
                  onClick={handleDraw}
                  disabled={isDrawing || items.length === 0}
                  size="lg"
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white gap-2 text-lg px-8 py-6 rounded-xl shadow-lg hover:shadow-xl transition-all"
                >
                  <Sparkles className="size-5" />
                  {t("draw")}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <Separator />

      {items.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <p>{t("noItems")}</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <BucketDrawCard
              key={item.id}
              item={item}
              onEdit={handleEdit}
              onDelete={(i) => setDeleteTarget(i)}
            />
          ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingItem ? t("editItem") : t("addItem")}</DialogTitle>
            <DialogDescription className="sr-only">
              {editingItem ? t("editItem") : t("addItem")}
            </DialogDescription>
          </DialogHeader>
          <BucketItemForm
            item={editingItem}
            onSubmit={handleSubmit}
            onCancel={() => setFormOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>{t("deleteItem")}</DialogTitle>
            <DialogDescription>{t("deleteConfirm")}</DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 pt-4">
            <Button variant="outline" className="flex-1" onClick={() => setDeleteTarget(null)}>
              {tCommon("cancel")}
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              onClick={() => deleteTarget && handleDelete(deleteTarget)}
            >
              {tCommon("delete")}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <ReturnJustificationModal
        open={showReturn}
        onOpenChange={setShowReturn}
        onSubmit={handleReturn}
      />
    </div>
  );
}
