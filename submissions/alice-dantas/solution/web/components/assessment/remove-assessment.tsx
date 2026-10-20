"use client";

import { Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ASSISTED } from "@/copy/assisted";

/** Remover a avaliação de uma oportunidade: botão só com ícone e, antes de apagar, uma janela de confirmação, porque
 * as respostas só existem neste navegador. */
export function RemoveAssessment({ id, onRemove }: { id: string; onRemove: () => void }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button size="icon-sm" variant="ghost" className="text-destructive hover:text-destructive"
                  aria-label={ASSISTED.remove.label(id)} onClick={() => setOpen(true)}>
            <Trash2 aria-hidden />
          </Button>
        </TooltipTrigger>
        <TooltipContent>{ASSISTED.remove.button}</TooltipContent>
      </Tooltip>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent showCloseButton={false} className="gap-5 rounded-3xl sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold">{ASSISTED.remove.title}</DialogTitle>
            <DialogDescription>{ASSISTED.remove.body}</DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-row justify-end gap-2">
            <Button variant="secondary" className="h-10 rounded-full px-5" onClick={() => setOpen(false)}>
              {ASSISTED.remove.cancel}
            </Button>
            <Button variant="destructive" className="h-10 rounded-full px-5"
                    onClick={() => { setOpen(false); onRemove(); }}>
              {ASSISTED.remove.confirm}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
