import Container from "@/components/ui/container";
import Link from "next/link";
import Image from "next/image";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/60 bg-white/80 backdrop-blur">
      <Container className="flex items-center justify-between py-3">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/logo.svg" alt="Hola" width={28} height={28} />
          <span className="text-lg font-semibold tracking-tight">Hola</span>
        </Link>

        <nav className="hidden items-center gap-7 md:flex">
          <a href="#features" className="text-sm font-medium text-slate-700 hover:text-slate-900">Características</a>
          <a href="#how" className="text-sm font-medium text-slate-700 hover:text-slate-900">Cómo Funciona</a>
          <a href="#about" className="text-sm font-medium text-slate-700 hover:text-slate-900">Acerca de</a>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <a href="/demo" className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700">Probar demo</a>
          <a href="#" className="rounded-md bg-orange-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-orange-700">Comenzar Gratis</a>
        </div>

        <button className="md:hidden inline-flex items-center justify-center rounded-md p-2 hover:bg-slate-100" aria-label="Abrir menú">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 6h16M4 12h16M4 18h16" stroke="#0f172a" strokeWidth="2" strokeLinecap="round"/></svg>
        </button>
      </Container>
    </header>
  );
}
