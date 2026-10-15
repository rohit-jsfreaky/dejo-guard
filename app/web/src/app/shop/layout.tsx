import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import s from "./shop.module.css";

export const metadata: Metadata = {
  title: "Sandbox shop · Dejo Guard",
  description: "A sandbox bookshop made by Dejo Guard to test a browser agent against real checkout pages. No real store, no real money.",
  robots: { index: false },
};

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={s.banner}>
        Sandbox shop made by Dejo Guard · not a real store · no real money · only the test card 4242 4242 4242 4242 works
      </div>
      <header className={s.top}>
        <div className={s.topIn}>
          <a className={s.brand} href="/shop">
            <Logo size={20} />
            Paperleaf <small>sandbox</small>
          </a>
          <nav className={s.nav}>
            <a href="/shop">Books</a>
            <a href="/shop/cart">Cart</a>
            <a href="/shop/orders">Orders</a>
            <a href="/shop/lab">Attack lab</a>
            <a href="/">Dejo Guard</a>
          </nav>
        </div>
      </header>
      <main className={s.main}>{children}</main>
    </>
  );
}
