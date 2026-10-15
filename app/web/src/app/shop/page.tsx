import { inr, search } from "@/lib/shop/catalog";
import { Cover } from "./Cover";
import s from "./shop.module.css";

// A GET search form on purpose: it only builds a URL, so Dejo Guard names it `navigate`, not a submit.
export default async function ShopHome({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = "" } = await searchParams;
  const books = search(q);
  return (
    <>
      <h1 className={s.h1}>Books</h1>
      <p className={s.lead}>Paperback and hardcover, delivered across India. Prices in rupees.</p>
      <form className={s.search} method="get" action="/shop" role="search">
        <input className={s.input} type="search" name="q" defaultValue={q} placeholder="Search by title or author" aria-label="Search books" />
        <button className="btn btnInk" type="submit">
          Search
        </button>
      </form>
      {books.length === 0 && <p className={s.lead}>No books match “{q}”.</p>}
      <div className={s.grid}>
        {books.map((b) => (
          <a key={b.id} className={s.card} href={`/shop/p/${b.id}`}>
            <Cover book={b} />
            <div className={s.meta}>
              <h3>{b.title}</h3>
              <p>{b.author}</p>
              <div className={s.price}>{inr(b.price)}</div>
            </div>
          </a>
        ))}
      </div>
    </>
  );
}
