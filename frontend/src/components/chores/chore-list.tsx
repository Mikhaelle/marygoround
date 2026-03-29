"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ChoreCard } from "./chore-card";
import { Plus, Search } from "lucide-react";
import type { Chore } from "@/types/chore";

interface ChoreListProps {
  chores: Chore[];
  onAdd: () => void;
  onEdit: (chore: Chore) => void;
  onDelete: (chore: Chore) => void;
}

/** Searchable grid of chore cards with an add button. */
export function ChoreList({ chores, onAdd, onEdit, onDelete }: ChoreListProps) {
  const t = useTranslations("chores");
  const tCommon = useTranslations("common");
  const [search, setSearch] = useState("");

  const filteredChores = chores.filter(
    (chore) =>
      chore.name.toLowerCase().includes(search.toLowerCase()) ||
      chore.category?.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder={tCommon("search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button
          onClick={onAdd}
          className="bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5 shrink-0"
        >
          <Plus className="size-4" />
          {t("addChore")}
        </Button>
      </div>

      {filteredChores.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <p>{chores.length === 0 ? t("noChores") : tCommon("noResults")}</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filteredChores.map((chore) => (
            <ChoreCard key={chore.id} chore={chore} onEdit={onEdit} onDelete={onDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
