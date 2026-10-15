import type { Book } from "@/lib/shop/catalog";
import s from "./shop.module.css";

export function Cover({ book }: { book: Book }) {
  return (
    <div className={s.cover} style={{ background: book.cover, color: book.ink }}>
      <b>{book.title}</b>
      <span>{book.author}</span>
    </div>
  );
}
