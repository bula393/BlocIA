import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { create } from 'zustand';
import { getProfile, updateProfile } from '../../api/profile';

export const usePerfilDraft = create<{ draftOpen: boolean; setDraftOpen: (value: boolean) => void }>((set) => ({
  draftOpen: false,
  setDraftOpen: (value) => set({ draftOpen: value })
}));

export function usePerfil() {
  const queryClient = useQueryClient();
  const profile = useQuery({ queryKey: ['profile'], queryFn: getProfile });
  const update = useMutation({
    mutationFn: updateProfile,
    onSuccess: (data) => queryClient.setQueryData(['profile'], data)
  });
  return { profile, update };
}
