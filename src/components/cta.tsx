import Container from "@/components/ui/container";

export default function CTA() {
  return (
    <section className="relative my-8 md:my-14">
      <Container>
        <div className="overflow-hidden rounded-3xl bg-blue-700 px-6 py-12 text-center text-white shadow-[0_16px_40px_-10px_rgba(11,99,229,0.5)] md:px-12">
          <h2 className="text-3xl font-bold md:text-4xl">
            Únete a la revolución de la comunicación inclusiva
          </h2>
          <p className="mx-auto mt-3 max-w-3xl text-blue-100">
            Miles de personas ya están usando Hola para conectar sin barreras. Comienza gratis hoy mismo.
          </p>
          <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href="#"
              className="rounded-xl bg-orange-500 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-orange-600"
            >
              Comenzar Gratis
            </a>
            <a
              href="#"
              className="rounded-xl border border-white/70 px-6 py-3 text-base font-semibold text-white/95 hover:bg-white/10"
            >
              Contactar Ventas
            </a>
          </div>
        </div>
      </Container>
    </section>
  );
}
