import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { create } from 'zustand';
import { confirmEmailVerification, getEmailVerification, listTechnicalProviders, removeProviderToken, requestEmailVerification, saveProviderToken } from '../../api/technicalProfile';
import { ApiRequestError } from '../../api/client';

export const useTokenDraft = create<{ tokenDraft: string; setTokenDraft: (value: string) => void }>((set) => ({
  tokenDraft: '',
  setTokenDraft: (value) => set({ tokenDraft: value })
}));

export function usePerfilTecnico() {
  const queryClient = useQueryClient();
  const providers = useQuery({ queryKey: ['technical-profile'], queryFn: listTechnicalProviders });
  const verification = useQuery({ queryKey: ['technical-email-verification'], queryFn: getEmailVerification, retry: false });
  const requestVerification = useMutation({
    mutationFn: requestEmailVerification,
    onSuccess: (status) => queryClient.setQueryData(['technical-email-verification'], status),
    onError: () => { void queryClient.invalidateQueries({ queryKey: ['technical-email-verification'] }); }
  });
  const confirmVerification = useMutation({
    mutationFn: confirmEmailVerification,
    onSuccess: (status) => queryClient.setQueryData(['technical-email-verification'], status),
    onError: () => { void queryClient.invalidateQueries({ queryKey: ['technical-email-verification'] }); }
  });
  const save = useMutation({
    mutationFn: ({ providerId, token }: { providerId: string; token: string }) => saveProviderToken(providerId, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['technical-profile'] });
      queryClient.invalidateQueries({ queryKey: ['available-models'] });
      queryClient.invalidateQueries({ queryKey: ['chat-providers'] });
      queryClient.invalidateQueries({ queryKey: ['chat-models'] });
      queryClient.invalidateQueries({ queryKey: ['usage-today'] });
    },
    onError: (error) => {
      if (error instanceof ApiRequestError && error.status === 403) {
        void queryClient.invalidateQueries({ queryKey: ['technical-email-verification'] });
      }
    }
  });
  const remove = useMutation({
    mutationFn: removeProviderToken,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['technical-profile'] });
      queryClient.invalidateQueries({ queryKey: ['available-models'] });
      queryClient.invalidateQueries({ queryKey: ['chat-providers'] });
      queryClient.invalidateQueries({ queryKey: ['chat-models'] });
      queryClient.invalidateQueries({ queryKey: ['usage-today'] });
    }
  });
  return { providers, save, remove, verification, requestVerification, confirmVerification };
}
