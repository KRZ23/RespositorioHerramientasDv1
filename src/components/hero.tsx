import Container from "@/components/ui/container";

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden">
      <Container className="pb-8 pt-14 text-center md:pt-20">
        <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-sm text-slate-700 shadow-sm">
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-orange-500/10">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2" stroke="#f97316" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </span>
          Traducción en tiempo real
        </div>

        <h1 className="mt-6 text-4xl font-extrabold leading-tight tracking-tight md:text-6xl">
          Conecta sin barreras
          <br className="hidden md:block" /> con lenguaje de señas
        </h1>
        <p className="mx-auto mt-5 max-w-3xl text-lg text-slate-600">
          Hola traduce lenguaje de señas en tiempo real, haciendo la comunicación accesible para todos.
          Rompe las barreras del lenguaje con tecnología inteligente.
        </p>

        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a href="/demo" className="rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700">Probar Ahora</a>
          <a href="#features" className="rounded-xl border border-slate-200 bg-white px-6 py-3 text-base font-semibold text-slate-900 shadow-sm hover:bg-slate-50">Ver Características</a>
        </div>
      </Container>

      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="mx-auto h-[520px] w-[90%] max-w-6xl rounded-[40px] bg-gradient-to-b from-blue-600/5 via-transparent to-transparent"></div>
      </div>
    </section>
  );
}
