// Send www.singingbowlaustralia.com to the bare domain (one canonical host for SEO).
export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname === 'www.singingbowlaustralia.com') {
    url.hostname = 'singingbowlaustralia.com';
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
