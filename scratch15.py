with open('frontend/src/app/dashboard/businesses/[id]/inbox/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_set_messages = '''        setMessages(prev => {
          const newMessages = [...prev];
          data.forEach((serverMsg: Message) => {
            const existingIdx = newMessages.findIndex(m => m.id === serverMsg.id);
            if (existingIdx >= 0) {
              newMessages[existingIdx] = serverMsg;
            } else {
              newMessages.push(serverMsg);
            }
          });
          return newMessages.filter(m => {
            if (m.id.startsWith('temp-')) {
              const isDuplicate = data.some((sm: Message) => sm.content === m.content && sm.sender_type === m.sender_type);
              return !isDuplicate;
            }
            return true;
          }).sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });'''

new_set_messages = '''        setMessages(prev => {
          const tempMessages = prev.filter(m => m.id.startsWith('temp-') && m.conversation_id === conversationId);
          const newMessages = [...data];
          tempMessages.forEach(tempM => {
            const isDuplicate = data.some((sm: Message) => sm.content === tempM.content && sm.sender_type === tempM.sender_type);
            if (!isDuplicate) {
              newMessages.push(tempM);
            }
          });
          return newMessages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });'''

if old_set_messages in content:
    content = content.replace(old_set_messages, new_set_messages)
    with open('frontend/src/app/dashboard/businesses/[id]/inbox/page.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced!")
else:
    print("Not found!")
