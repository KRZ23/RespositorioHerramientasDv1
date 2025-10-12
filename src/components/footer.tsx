import Container from "@/components/ui/container";
import Image from "next/image";

export default function Footer() {
  return (
    <footer id="about" className="mt-10 pb-10 border-t border-slate-200">
      <Container className="flex flex-col items-center justify-between gap-4 pt-6 text-sm text-slate-500 md:flex-row">
        <div className="flex items-center gap-2">
          <Image src="/logo.svg" alt="Hola" width={24} height={24} />
          <span>© 2025 Hola. Todos los derechos reservados.</span>
        </div>
        <div className="flex items-center gap-6">
          <a className="hover:text-slate-700" href="#">Privacidad</a>
          <a className="hover:text-slate-700" href="#">Términos</a>
          <a className="hover:text-slate-700" href="#">Soporte</a>
          <a className="hover:text-slate-700" href="#">Blog</a>
        </div>
      </Container>
    </footer>
  );
}
