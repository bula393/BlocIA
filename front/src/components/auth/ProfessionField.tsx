const professions = [
  'Estudiante',
  'Docente',
  'Desarrollador/a de software',
  'Diseñador/a',
  'Profesional de salud',
  'Abogado/a',
  'Contador/a',
  'Administrativo/a',
  'Comerciante',
  'Emprendedor/a',
  'Investigador/a',
  'Varios trabajos',
  'Otro'
];

type ProfessionFieldProps = {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
};

export function ProfessionField({ value, onChange, required = false }: ProfessionFieldProps) {
  const options = value && !professions.includes(value) ? [...professions, value] : professions;

  return (
    <label>
      Profesión
      <select value={value} onChange={(event) => onChange(event.target.value)} required={required}>
        {!value && <option value="" disabled>Seleccioná una opción</option>}
        {options.map((profession) => <option key={profession} value={profession}>{profession}</option>)}
      </select>
    </label>
  );
}
