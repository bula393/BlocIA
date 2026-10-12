import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { disconnectGoogle, getGoogleConnection, getGoogleProjects, selectGoogleProject, startGoogleConnection } from '../../api/providerAccounts';

export function useGoogleConnection() {
  const cache = useQueryClient();
  const status = useQuery({ queryKey: ['google-connection'], queryFn: getGoogleConnection, retry: false });
  const projects = useQuery({ queryKey: ['google-projects', status.data?.email], queryFn: getGoogleProjects, enabled: Boolean(status.data?.connected && !status.data.needsReconnect && status.data.available), retry: false });
  const refresh = () => {
    for (const key of ['technical-profile', 'available-models', 'chat-providers', 'chat-models', 'google-connection']) {
      void cache.invalidateQueries({ queryKey: [key] });
    }
  };
  const start = useMutation({ mutationFn: startGoogleConnection, onSuccess: ({ authorizationUrl }) => window.location.assign(authorizationUrl) });
  const select = useMutation({ mutationFn: selectGoogleProject, onSuccess: (result) => { cache.setQueryData(['google-connection'], result); refresh(); } });
  const disconnect = useMutation({ mutationFn: disconnectGoogle, onSuccess: () => {
    cache.removeQueries({ queryKey: ['google-projects'] });
    cache.setQueryData(['google-connection'], { ...status.data, connected: false, ready: false, email: null, projectId: null, projectName: null, needsReconnect: false });
    refresh();
  } });
  return { status, projects, start, select, disconnect };
}
