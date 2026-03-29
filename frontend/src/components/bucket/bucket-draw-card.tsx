"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2 } from "lucide-react";
import type { BucketItem } from "@/types/bucket";

interface BucketDrawCardProps {
  item: BucketItem;
  onEdit: (item: BucketItem) => void;
  onDelete: (item: BucketItem) => void;
}

/** Card for a bucket item in the pool showing name, description, and category. */
export function BucketDrawCard({ item, onEdit, onDelete }: BucketDrawCardProps) {
  const t = useTranslations("bucket");

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-purple-200 dark:hover:border-purple-800">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-foreground truncate">{item.name}</h3>
            {item.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{item.description}</p>
            )}
            {item.category && (
              <Badge variant="secondary" className="mt-2">
                {item.category}
              </Badge>
            )}
          </div>

          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button variant="ghost" size="icon-sm" onClick={() => onEdit(item)}>
              <Pencil className="size-3.5" />
              <span className="sr-only">{t("editItem")}</span>
            </Button>
            <Button
              variant="ghost"
              size="icon-sm"
              className="hover:text-destructive"
              onClick={() => onDelete(item)}
            >
              <Trash2 className="size-3.5" />
              <span className="sr-only">{t("deleteItem")}</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
