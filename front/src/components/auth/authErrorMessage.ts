type AuthAction = 'login' | 'register';

export function authErrorMessage(error: unknown, action: AuthAction) {
  const message = error instanceof Error ? error.message : '';
  const status = typeof error === 'object' && error !== null && 'status' in error
    && typeof error.status === 'number'
    ? error.status
    : undefined;

  if (action === 'register' && /already registered/i.test(message)) {
    return 'Ya existe una cuenta con ese correo. Iniciá sesión o probá con otro correo.';
  }
  if (action === 'login' && /invalid credentials/i.test(message)) {
    return 'El correo o la contraseña no coinciden. Revisá los datos e intentá de nuevo.';
  }
  if (action === 'register' && /password must include/i.test(message)) {
    return 'La contraseña necesita 10 caracteres, una letra, un número y un símbolo. Evitá incluir tu correo.';
  }

  if (status !== undefined) {
    if (action === 'login' && status === 401) {
      return 'El correo o la contraseña no coinciden. Revisá los datos e intentá de nuevo.';
    }
    if (action === 'register' && status === 409) {
      return 'Ya existe una cuenta con ese correo. Iniciá sesión o probá con otro correo.';
    }
    if (action === 'register' && status === 400 && /password must include/i.test(message)) {
      return 'La contraseña necesita 10 caracteres, una letra, un número y un símbolo. Evitá incluir tu correo.';
    }
    if (status >= 500) {
      return 'El servicio no está disponible ahora. Conservamos tus datos; probá de nuevo en unos minutos.';
    }
    if (action === 'register') {
      return 'Revisá el correo, la contraseña, la edad y la profesión antes de volver a intentar.';
    }
  }

  if (error instanceof TypeError || (error instanceof Error && /failed to fetch|networkerror|fetch failed/i.test(error.message))) {
    return 'No pudimos conectar con BloqIA. Conservamos tus datos; volvé a intentar cuando el servicio esté disponible.';
  }

  return action === 'login'
    ? 'No se pudo iniciar sesión. Revisá el correo y la contraseña e intentá de nuevo.'
    : 'No se pudo crear la cuenta. Revisá los datos e intentá de nuevo.';
}
