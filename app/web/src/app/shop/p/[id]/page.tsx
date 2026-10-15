import { notFound } from "next/navigation";
import { BOOKS, bookById, inr } from "@/lib/shop/catalog";
import { AddToCart } from "../../AddToCart";
import { Cover } from "../../Cover";
import s from "../../shop.module.css";

export function generateStaticParams() {
  return BOOKS.map((b) => ({ id: b.id }));
}

export default async function BookPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const book = bookById(id);
  if (!book) notFound();
  const others = BOOKS.filter((b) => b.id !== id).slice(0, 3);
  return (
    <div className={s.product}>
      <Cover book={book} />
      <div>
        <h1 className={s.h1}>{book.title}</h1>
        <p className={s.lead}>{book.author}</p>
        <div className={s.price} style={{ fontSize: 22, marginTop: 18 }}>
          {inr(book.price)}
        </div>
        <p className={s.lead} style={{ marginTop: 16, maxWidth: 520 }}>
          {book.blurb}
        </p>
        <AddToCart id={book.id} />
        <p className={s.note} style={{ marginTop: 36 }}>
          Also on sale:{" "}
          {others.map((b, i) => (
            <span key={b.id}>
              {i > 0 && " · "}
              <a href={`/shop/p/${b.id}`}>{b.title}</a>
            </span>
          ))}
        </p>
      </div>
    </div>
  );
}
