"use client";

import { useState, type FormEvent } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import type { BucketItem, CreateBucketItemRequest } from "@/types/bucket";

interface BucketItemFormProps {
  item?: BucketItem | null;
  onSubmit: (data: CreateBucketItemRequest) => Promise<void>;
  onCancel: () => void;
}

/** Form for creating or editing a bucket item. */
export function BucketItemForm({ item, onSubmit, onCancel }: BucketItemFormProps) {
  const t = useTranslations("bucket");
  const tCommon = useTranslations("common");

  const [name, setName] = useState(item?.name ?? "");
  const [description, setDescription] = useState(item?.description ?? "");
  const [category, setCategory] = useState(item?.category ?? "");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        category: category.trim() || undefined,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="item-name">{t("itemName")}</Label>
        <Input
          id="item-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={t("itemNamePlaceholder")}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="item-description">{t("description")}</Label>
        <Textarea
          id="item-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder={t("descriptionPlaceholder")}
          rows={3}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="item-category">{t("category")}</Label>
        <Input
          id="item-category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder={t("categoryPlaceholder")}
        />
      </div>

      <div className="flex gap-3 pt-2">
        <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
          {tCommon("cancel")}
        </Button>
        <Button
          type="submit"
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white"
          disabled={isSubmitting || !name.trim()}
        >
          {isSubmitting && <Loader2 className="size-4 animate-spin" />}
          {tCommon("save")}
        </Button>
      </div>
    </form>
  );
}
