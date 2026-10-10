import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { ChatWorkspace } from '../features/chat/components/ChatWorkspace';
import { useChatController } from '../features/chat/useChatController';

export function NuevoChat() {
  const chat = useChatController();
  return <ChasisBloqIA title="Chat" activePath="/nuevo-chat" chatLocked={Boolean(chat.usageLock?.blocked)}
    mobileSection={chat.historyOpen || chat.activeId ? 'chats' : 'home'}
    onMobileChatNavigation={(section) => { if (section === 'chats') chat.setHistoryOpen(true); else chat.selectConversation(null); }}>
    <ChatWorkspace chat={chat} />
  </ChasisBloqIA>;
}
