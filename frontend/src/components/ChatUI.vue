<template>
  <div class="chat-context-row redesigned-row">
    <div class="chat-main-col redesigned-main-col">
      <div class="chat-ui card shadow-sm redesigned-chat-ui" aria-label="Chat interface">
        <div class="card-header d-flex align-items-center justify-content-between">
          <span class="fw-bold">Chatbot</span>
          <select v-model="queryType" class="form-select form-select-sm w-auto ms-2" aria-label="Query type">
            <option v-for="type in queryTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div class="context-toggle-bar d-flex align-items-center justify-content-end p-2">
          <button
            class="btn add-context-btn"
            :class="{ toggled: showContext }"
            @click="showContext = !showContext"
            :aria-pressed="showContext"
            aria-label="Add Context"
          >
            <span v-if="showContext">Hide Context</span>
            <span v-else>Add Context</span>
          </button>
        </div>
        <div class="card-body chat-history redesigned-chat-history" aria-live="polite">
          <div v-for="(msg, i) in messages" :key="i" :class="['mb-2', msg.role === 'user' ? 'text-end' : 'text-start']">
            <span :class="['badge', msg.role === 'user' ? 'bg-primary' : 'bg-secondary']" :aria-label="msg.role === 'user' ? 'You' : 'Bot'">
              {{ msg.role === 'user' ? 'You' : 'Bot' }}
            </span>
            <span class="ms-2" v-html="msg.text"></span>
          </div>
          <div v-if="isStreaming" class="text-muted fst-italic" aria-live="polite" aria-atomic="true">
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Bot is typing...
          </div>
        </div>
        <div class="card-footer bg-light redesigned-footer">
          <form @submit.prevent="sendMessage" class="d-flex flex-column flex-md-row gap-2" autocomplete="off">
            <input v-model="input" class="form-control" :aria-label="'Type your message'" :disabled="isStreaming" required maxlength="500" />
            <button class="btn btn-primary" type="submit" :disabled="isStreaming || !input.trim()" aria-label="Send message">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
    <ContextProvider v-if="showContext" class="context-col redesigned-context-col context-provider-animated" @update:contextFiles="onContextFilesUpdate" @close="showContext = false" />
  </div>
</template>

<script lang="ts" setup>
 import { ref, onMounted, watch } from 'vue';
import { useCodeHighlight } from '../composables/useCodeHighlight';

 interface Message {
  text: string;
  role: 'user' | 'bot';
 }

const input = ref('');
const messages = ref<Message[]>([]);
const isStreaming = ref(false);
const queryType = ref('qa');
const queryTypes = [
  { value: 'qa', label: 'Q&A' },
  { value: 'summarize', label: 'Summarize' },
  { value: 'code', label: 'Code' },
  { value: 'explain', label: 'Explain' },
];
const showContext = ref(false);
const contextFiles = ref<Array<{ name: string; content: string }>>([]);

function onContextFilesUpdate(files: Array<{ name: string; content: string }>) {
  // Defensive: always replace with a new array
  contextFiles.value = [...files];
  // Debug: log update
  console.log('DEBUG onContextFilesUpdate:', JSON.stringify(contextFiles.value));
}


// Use composable for code highlighting and copy buttons
const { highlightAllCode } = useCodeHighlight();

onMounted(highlightAllCode);

watch(messages, highlightAllCode);

async function sendMessage() {
  if (!input.value.trim()) return;
  let prompt = input.value.trim();
  // Debug: log contextFiles before prepending
  console.log('DEBUG contextFiles:', JSON.stringify(contextFiles.value));
  // If context is active and files are selected, prepend as specified
  if (showContext.value && contextFiles.value.length > 0) {
    if (contextFiles.value.length <= 1) {
      prompt = `${contextFiles.value[0].content}\nUse the above context to answer the below:\n${prompt}`;
      // Debug: log single-file prompt
      console.log('DEBUG single-file prompt:', prompt);
    } else {
      const contextBlock = contextFiles.value.map(f => `${f.name}:\n${f.content}\n`).join('\n');
      prompt = `${contextBlock}\nUse the above file contents as context to answer the below:\n\n${prompt}`;
      // Debug: log multi-file prompt
      console.log('DEBUG multi-file prompt:', prompt);
    }
  }
  // Debug: log final prompt before sending
  console.log('DEBUG final prompt to backend:', prompt);
  messages.value.push({ role: 'user', text: input.value });
  const userMsg = prompt;
  const selectedType = queryType.value;
  input.value = '';
  isStreaming.value = true;
  let botMsgIdx = messages.value.length;
  // Call backend
  let botText = '';
  try {
    const res = await fetch('http://localhost:8000/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'demo', text: userMsg, query_type: selectedType })
    });
    const data = await res.json();
    botText = data.response || '[No response]';
  } catch (e) {
    botText = '[Error contacting backend]';
  }
  // Simulate streaming: reveal one word at a time
  const words = botText.split(' ');
  let current = '';
  for (let i = 0; i < words.length; i++) {
    current += (i > 0 ? ' ' : '') + words[i];
    await new Promise(r => setTimeout(r, 40));
    if (messages.value.length > botMsgIdx && messages.value[botMsgIdx].role === 'bot') {
      messages.value[botMsgIdx].text = current;
    } else {
      messages.value.push({ text: current, role: 'bot' });
    }
    highlightAllCode();
  }
  isStreaming.value = false;
}
</script>

<style scoped>
html, body, #app {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  background: #f8f9fa;
}
.chat-context-row.redesigned-row {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background: #f8f9fa;
}
.chat-main-col.redesigned-main-col {
  display: flex;
  align-items: stretch;
  justify-content: center;
  flex: 1 1 0;
  min-width: 320px;
  max-width: 80vw;
}
.chat-ui.redesigned-chat-ui {
  width: 100%;
  min-width: 320px;
  max-width: 80vw;
  height: 100%;
  max-height: 100vh;
  margin: 0;
  border-radius: 0.7rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 24px 0 rgba(0,0,0,0.08);
  background: #fff;
}
.chat-history.redesigned-chat-history {
  flex: 1 1 auto;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
  background: #f8f9fa;
  border-radius: 0;
  padding: 1rem;
}
.card-footer.redesigned-footer {
  padding: 0.5rem 1rem;
}
.context-col.redesigned-context-col {
  display: flex;
  align-items: stretch;
  justify-content: flex-start;
  flex: 0 1 340px;
  min-width: 260px;
  max-width: 80vw;
  height: 100%;
  margin-left: 1.5rem;
  margin-top: 0;
}
.context-provider-animated {
  animation: fadeInRight 0.3s;
}
@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(40px); }
  to { opacity: 1; transform: translateX(0); }
}
@media (max-width: 900px) {
  .chat-context-row.redesigned-row {
    flex-direction: column;
    align-items: stretch;
    height: 100vh;
    width: 100vw;
  }
  .chat-main-col.redesigned-main-col {
    max-width: 100vw;
    min-width: 0;
  }
  .chat-ui.redesigned-chat-ui {
    max-width: 100vw;
    min-width: 0;
    height: 60vh;
    max-height: 60vh;
  }
  .context-col.redesigned-context-col {
    margin-left: 0;
    margin-top: 1rem;
    max-width: 100vw;
    min-width: 0;
    height: 40vh;
  }
}
@media (max-width: 600px) {
  .chat-context-row.redesigned-row {
    flex-direction: column;
    align-items: stretch;
    height: 100vh;
    width: 100vw;
  }
  .chat-main-col.redesigned-main-col {
    max-width: 100vw;
    min-width: 0;
  }
  .chat-ui.redesigned-chat-ui {
    max-width: 100vw;
    min-width: 0;
    height: 55vh;
    max-height: 55vh;
  }
  .context-col.redesigned-context-col {
    margin-left: 0;
    margin-top: 1rem;
    max-width: 100vw;
    min-width: 0;
    height: 45vh;
  }
}
</style>
