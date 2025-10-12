import Container from "@/components/ui/container";

const steps = [
  { title: "Activa tu cámara", desc: "Permite el acceso para comenzar a capturar las señas." },
  { title: "Haz tus señas", desc: "Comunícate naturalmente frente a la cámara." },
  { title: "Recibe la traducción", desc: "Obtén texto o voz en tiempo real." },
];

export default function Steps() {
  return (
    <section id="how" className="py-12">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Tan simple como 1, 2, 3</h2>
          <p className="mt-3 text-slate-600">Comienza a comunicarte en segundos</p>
        </div>
        <ol className="mx-auto mt-8 grid max-w-5xl gap-6 sm:grid-cols-3">
          {steps.map((s, i) => (
            <li key={s.title} className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <div className="mx-auto mb-3 grid h-10 w-10 place-content-center rounded-full bg-blue-600 text-white">{i + 1}</div>
              <h3 className="text-base font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{s.desc}</p>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  );
}
