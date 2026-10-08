export const classificationLabels = { no_personal: 'Consulta general', personal_informativa: 'Análisis personal', personal_decision: 'Decisión personal' };
export const chatIdeas = [
  { title: 'Entender un tema', prompt: 'Explicame qué es una API con un ejemplo sencillo.' },
  { title: 'Ordenar mis ideas', prompt: '¿Qué factores debería considerar antes de cambiar de trabajo?' },
  { title: 'Evaluar una decisión', prompt: '¿Debería estudiar programación o diseño?' }
];

export function providerLabel(providerId: string, fallback: string) {
  const known: Record<string, string> = { local: 'En tu equipo', google: 'Google AI', groq: 'Groq', openrouter: 'OpenRouter', openai: 'OpenAI', anthropic: 'Anthropic' };
  return known[providerId] ?? fallback.replace(/\s*·\s*/g, ', ');
}
