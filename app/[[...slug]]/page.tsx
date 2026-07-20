import Mockup from "../mockup";

export default async function Page({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug = [] } = await params;
  return <Mockup route={`/${slug.join("/")}`} />;
}
