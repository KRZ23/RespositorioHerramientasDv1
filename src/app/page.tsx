import Navbar from "@/components/navbar";
import Hero from "@/components/hero";
import Features from "@/components/features";
import Steps from "@/components/steps";
import CTA from "@/components/cta";
import Footer from "@/components/footer";
import Container from "@/components/ui/container";

export default function Page() {
  return (
    <main>
      <Navbar />
      <Hero />
      <Container className="mt-6 md:mt-8">
        <div
          id="demo"
          className="rounded-3xl border border-slate-200 bg-white p-4 shadow-[0_10px_40px_-15px_rgba(0,0,0,0.15)] md:p-6"
        >
          <div className="aspect-video w-full rounded-2xl bg-slate-100 grid place-content-center text-slate-500">
            <div className="flex items-center gap-2 text-base font-medium">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M15 10l4-3v10l-4-3M5 7h8v10H5z" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Vista previa — integraremos la cámara en /demo
            </div>
          </div>
          <p className="mt-3 text-center text-sm text-slate-500">
            La demo de cámara se carga en una página separada para proteger rendimiento y permisos.
          </p>
        </div>
      </Container>
      <Features />
      <Steps />
      <CTA />
      <Footer />
    </main>
  );
}
