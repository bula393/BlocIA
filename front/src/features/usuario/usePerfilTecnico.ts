import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { create } from 'zustand';
import { listTechnicalProviders, removeProviderToken, saveProviderToken } from '../../api/technicalProfile';

export const useTokenDraft = create<{ tokenDraft: string; setTokenDraft: (value: string) => void }>((set) => ({
  tokenDraft: '',
  setTokenDraft: (value) => set({ tokenDraft: value })
}));

export function usePerfilTecnico() {
  const queryClient = useQueryClient();
  const providers = useQuery({ queryKey: ['technical-profile'], queryFn: listTechnicalProviders });
  const save = useMutation({
    mutationFn: ({ providerId, token }: { providerId: string; token: string }) => saveProviderToken(providerId, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['technical-profile'] })
  });
  const remove = useMutation({
    mutationFn: removeProviderToken,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['technical-profile'] })
  });
  return { providers, save, remove };
}
