import { FormEvent, useState } from 'react';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { CajonPerfil } from '../components/overlay/CajonPerfil';
import { usePerfil } from '../features/usuario/usePerfil';

export function Perfil() {
  const { profile, update } = usePerfil();
  const [age, setAge] = useState('');
  const [profession, setProfession] = useState('');
  const [displayName, setDisplayName] = useState('');

  function submit(event: FormEvent) {
    event.preventDefault();
    update.mutate({
      age: age ? Number(age) : undefined,
      profession: profession || undefined,
      displayName: displayName || undefined
    });
  }

  return (
    <ChasisBloqIA title="Perfil" activePath="/perfil">
      <h1>Perfil</h1>
      {profile.isLoading && <p>Cargando perfil...</p>}
      {profile.isError && <p className="bloq-error">No se pudo cargar el perfil.</p>}
      {profile.data && (
        <CajonPerfil>
          <p>Mail: {profile.data.mail}</p>
          <p>Edad: {profile.data.age}</p>
          <p>Profesion: {profile.data.profession}</p>
          <p>Ingreso: {profile.data.loginProviderStatus}</p>
          <p>Perfil tecnico: {profile.data.technicalProfileStatus}</p>
        </CajonPerfil>
      )}
      <form className="bloq-form" onSubmit={submit}>
        <label>Edad<input type="number" min={1} value={age} onChange={(event) => setAge(event.target.value)} /></label>
        <label>Profesion<input value={profession} onChange={(event) => setProfession(event.target.value)} /></label>
        <label>Nombre visible<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} /></label>
        <div className="bloq-actions">
          <button type="submit" data-primary="true">Guardar cambios</button>
        </div>
      </form>
      {update.isError && <p className="bloq-error">No se guardaron los cambios.</p>}
      {update.isSuccess && <p className="bloq-success">Perfil actualizado.</p>}
    </ChasisBloqIA>
  );
}
