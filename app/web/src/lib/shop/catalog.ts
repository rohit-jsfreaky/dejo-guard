// The sandbox shop's books. Prices are in rupees and nothing here can ever be paid for for real.
export type Book = { id: string; title: string; author: string; price: number; cover: string; ink: string; blurb: string };

export const BOOKS: Book[] = [
  { id: "atomic-habits", title: "Atomic Habits", author: "James Clear", price: 499, cover: "#e8efe6", ink: "#1f3a24", blurb: "Tiny changes, remarkable results. The paperback edition." },
  { id: "deep-work", title: "Deep Work", author: "Cal Newport", price: 399, cover: "#e6ebf2", ink: "#1d2c44", blurb: "Rules for focused success in a distracted world." },
  { id: "designing-data", title: "Designing Data-Intensive Applications", author: "Martin Kleppmann", price: 1899, cover: "#f1ece4", ink: "#3d2e14", blurb: "The big ideas behind reliable, scalable systems." },
  { id: "pragmatic", title: "The Pragmatic Programmer", author: "Hunt & Thomas", price: 1299, cover: "#ece8f2", ink: "#2c2140", blurb: "Your journey to mastery, 20th anniversary edition." },
  { id: "psychology-money", title: "The Psychology of Money", author: "Morgan Housel", price: 349, cover: "#f2efe2", ink: "#3a3412", blurb: "Timeless lessons on wealth, greed and happiness." },
  { id: "sapiens", title: "Sapiens", author: "Yuval Noah Harari", price: 599, cover: "#e5eeee", ink: "#173638", blurb: "A brief history of humankind." },
  { id: "clean-code", title: "Clean Code", author: "Robert C. Martin", price: 899, cover: "#eef0e6", ink: "#2b3214", blurb: "A handbook of agile software craftsmanship." },
  { id: "godaan", title: "गोदान (Godaan)", author: "Munshi Premchand", price: 199, cover: "#f2e9e4", ink: "#3f2418", blurb: "प्रेमचंद का अंतिम और सबसे प्रसिद्ध उपन्यास।" },
];

export const bookById = (id: string) => BOOKS.find((b) => b.id === id);

export function search(q: string): Book[] {
  const t = q.trim().toLowerCase();
  if (!t) return BOOKS;
  return BOOKS.filter((b) => `${b.title} ${b.author}`.toLowerCase().includes(t));
}

export const inr = (n: number) => `₹${n.toLocaleString("en-IN")}`;

// The only card the sandbox accepts. A real card number is refused and never stored.
export const TEST_CARD = "4242424242424242";
