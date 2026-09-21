import { useMutation } from '@tanstack/react-query';
import { register } from '../../api/auth';

export function useRegister() {
  return useMutation({
    mutationFn: ({ mail, password, age, profession }: { mail: string; password: string; age: number; profession: string }) =>
      register(mail, password, age, profession)
  });
}
