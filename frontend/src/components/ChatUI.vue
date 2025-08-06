<template>
  <div class="chat-ui card shadow-sm" aria-label="Chat interface">
    <div class="card-header d-flex align-items-center justify-content-between">
      <span class="fw-bold">Chatbot</span>
      <select v-model="queryType" class="form-select form-select-sm w-auto ms-2" aria-label="Query type">
        <option v-for="type in queryTypes" :key="type.value" :value="type.value">
          {{ type.label }}
        </option>
      </select>
    </div>
    <div class="card-body chat-history" aria-live="polite">
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
    <div class="card-footer bg-light">
      <form @submit.prevent="sendMessage" class="d-flex flex-column flex-md-row gap-2" autocomplete="off">
        <input v-model="input" class="form-control" :aria-label="'Type your message'" :disabled="isStreaming" required maxlength="500" />
        <button class="btn btn-primary" type="submit" :disabled="isStreaming || !input.trim()" aria-label="Send message">
          Send
        </button>
      </form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

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

async function sendMessage() {
  if (!input.value.trim()) return;
  messages.value.push({ text: input.value, role: 'user' });
  const userMsg = input.value;
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
  }
  isStreaming.value = false;
}
</script>

<style scoped>
.chat-ui {
  max-width: 600px;
  margin: 2rem auto;
}
.chat-history {
  min-height: 200px;
  max-height: 350px;
  overflow-y: auto;
  background: #f8f9fa;
  border-radius: 0.25rem;
  padding: 1rem;
}
@media (max-width: 600px) {
  .chat-ui {
    max-width: 100%;
    margin: 0.5rem;
  }
}
</style>
