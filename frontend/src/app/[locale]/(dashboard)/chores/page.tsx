"use client";

import { useCallback, useState } from "react";
import { useTranslations } from "next-intl";
import { useChores } from "@/lib/hooks/use-chores";
import { ChoreList } from "@/components/chores/chore-list";
import { ChoreForm } from "@/components/chores/chore-form";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import type { Chore, CreateChoreRequest } from "@/types/chore";

/** Chore management page with list, create/edit dialogs, and delete confirmation. */
export default function ChoresPage() {
  const t = useTranslations("chores");
  const tCommon = useTranslations("common");
  const { chores, isLoading, createChore, updateChore, deleteChore } = useChores();

  const [formOpen, setFormOpen] = useState(false);
  const [editingChore, setEditingChore] = useState<Chore | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Chore | null>(null);

  const handleAdd = useCallback(() => {
    setEditingChore(null);
    setFormOpen(true);
  }, []);

  const handleEdit = useCallback((chore: Chore) => {
    setEditingChore(chore);
    setFormOpen(true);
  }, []);

  const handleSubmit = useCallback(
    async (data: CreateChoreRequest) => {
      try {
        if (editingChore) {
          await updateChore(editingChore.id, data);
          toast.success(t("choreUpdated"));
        } else {
          await createChore(data);
          toast.success(t("choreCreated"));
        }
        setFormOpen(false);
        setEditingChore(null);
      } catch {
        toast.error(tCommon("error"));
      }
    },
    [editingChore, createChore, updateChore, t, tCommon],
  );

  const handleDelete = useCallback(
    async (chore: Chore) => {
      try {
        await deleteChore(chore.id);
        toast.success(t("choreDeleted"));
        setDeleteTarget(null);
      } catch {
        toast.error(tCommon("error"));
      }
    },
    [deleteChore, t, tCommon],
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
      <div>
        <h1 className="text-2xl font-bold text-foreground">{t("title")}</h1>
      </div>

      <ChoreList
        chores={chores}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={(chore) => setDeleteTarget(chore)}
      />

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingChore ? t("editChore") : t("addChore")}</DialogTitle>
            <DialogDescription className="sr-only">
              {editingChore ? t("editChore") : t("addChore")}
            </DialogDescription>
          </DialogHeader>
          <ChoreForm
            chore={editingChore}
            onSubmit={handleSubmit}
            onCancel={() => setFormOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>{t("deleteChore")}</DialogTitle>
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
    </div>
  );
}
