import Header from "./Header";

export default function Shell({ route, children, narrow = false }: { route: string; children: React.ReactNode; narrow?: boolean }) {
  return (
    <>
      <Header route={route} />
      <main className={narrow ? "page narrow" : "page"}>{children}</main>
    </>
  );
}