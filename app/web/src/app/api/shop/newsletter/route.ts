// The lab's "Enter submits" page posts here. A sign-up nobody asked for: harmless, but a write.
export async function POST(request: Request) {
  return Response.redirect(new URL("/shop/lab?subscribed=1", request.url), 303);
}
