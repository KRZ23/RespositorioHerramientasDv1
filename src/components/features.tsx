import Container from "@/components/ui/container";

const items = [
  {
    title: "Traducción en Tiempo Real",
    desc: "Interpreta señas instantáneamente con precisión y velocidad.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <rect x="4" y="5" width="10" height="14" rx="2" stroke="#0ea5e9" strokeWidth="2"/>
        <path d="M15 10l4-3v10l-4-3" stroke="#0ea5e9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    title: "Conversaciones Bidireccionales",
    desc: "De señas a texto y de texto a señas para una comunicación fluida.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M7 8h10M7 12h6M7 16h10" stroke="#fb923c" strokeWidth="2" strokeLinecap="round"/>
        <path d="M5 6v12l3-3h11" stroke="#fb923c" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    title: "Accesible para Todos",
    desc: "Interfaz intuitiva con alto contraste y soporte de teclado.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <circle cx="12" cy="7" r="3" stroke="#38bdf8" strokeWidth="2"/>
        <path d="M4 21l3.5-7H16.5L20 21" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    title: "Múltiples Idiomas de Señas",
    desc: "Diseñado para escalar a distintos idiomas de señas.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <circle cx="12" cy="12" r="9" stroke="#60a5fa" strokeWidth="2"/>
        <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" stroke="#60a5fa" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    title: "Aprendizaje Continuo",
    desc: "Mejora con feedback anónimo y controlado del usuario.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M3 11h6l2-3 2 6 2-4 4 1" stroke="#fb7185" strokeWidth="2" strokeLinecap="round"/>
        <path d="M4 18h16" stroke="#fb7185" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    title: "Privacidad por Diseño",
    desc: "Procesamiento on-device por defecto; permisos claros.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M6 10V7a6 6 0 0 1 12 0v3" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round"/>
        <rect x="4" y="10" width="16" height="10" rx="2" stroke="#f59e0b" strokeWidth="2"/>
      </svg>
    ),
  },
];

export default function Features() {
  return (
    <section id="features" className="py-10 md:py-16">
      <Container>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Características que marcan la diferencia</h2>
          <p className="mt-3 text-slate-600">Tecnología diseñada para hacer la comunicación más inclusiva y accesible</p>
        </div>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((f) => (
            <div key={f.title} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-colors hover:border-slate-300">
              <div className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100">{f.icon}</div>
              <h3 className="text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
