<template>
  <div class="context-provider redesigned-context-provider">
    <div class="context-header">
      <span class="fw-bold small-title">Context Provider</span>
      <button class="btn btn-sm btn-outline-secondary close-btn" @click="$emit('close')" aria-label="Close context provider">&times;</button>
    </div>
    <div class="context-controls">
      <label class="form-label form-label-sm mb-1">Select file(s) for context:</label>
      <div class="file-list-container">
        <div class="file-list">
          <div v-for="file in files" :key="file.name"
            :class="['file-item', { selected: selectedFiles.includes(file.name) }]"
            @click="onFileClick($event, file.name)">
            <span class="file-icon">{{ fileIcon(file.name) }}</span>
            <span class="file-name">{{ file.name }}</span>
          </div>
        </div>
      </div>
      <div v-if="selectedContents.length" class="context-content-container mt-2">
        <div class="context-content">
          <div v-for="file in selectedContents" :key="file.name" class="content-block mb-2">
            <div class="file-label">{{ file.name }}:</div>
            <pre class="context-pre">{{ file.content }}</pre>
          </div>
        </div>
      </div>
      <div v-else class="text-muted small mt-2">No file selected.</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';

const files = [
  { name: 'Resume.pdf', content: 'John Doe\nSoftware Engineer\nExperience: ...' },
  { name: 'ProjectPlan.docx', content: 'Project Plan\nMilestone 1: ...' },
  { name: 'Research.txt', content: 'AI research notes\n- LLMs\n- Transformers\n...' },
  { name: 'MeetingNotes.txt', content: 'Meeting Notes\n- Discussed roadmap\n- Action items...' },
  { name: 'Budget.xlsx', content: '2025 Budget\n- Salaries\n- Equipment\n- Travel...' },
  { name: 'Presentation.pptx', content: 'Q3 Presentation\nSlide 1: Overview\nSlide 2: Results...' },
  { name: 'Design.sketch', content: 'UI Design\n- Home page\n- Chat window...' },
  { name: 'Invoice001.pdf', content: 'Invoice #001\nAmount: $1,200\nDue: 2025-08-15' },
  { name: 'Summary.docx', content: 'Executive Summary\n- Key findings\n- Recommendations...' },
  { name: 'Script.js', content: 'function greet() {\n  console.log("Hello, world!");\n}' },
  { name: 'Data.csv', content: 'id,name,value\n1,Alice,10\n2,Bob,20' },
  { name: 'Manual.md', content: '# User Manual\n## Installation\n## Usage' },
  { name: 'Contract.pdf', content: 'Service Contract\nParties: ...\nTerms: ...' },
  { name: 'Logo.png', content: '[binary image data]' },
  { name: 'App.vue', content: '<template>\n  <div>Hello App</div>\n</template>' },
  { name: 'Dockerfile', content: 'FROM node:18\nCOPY . /app\nRUN npm install' },
  { name: 'README.md', content: '# Project README\nThis project is ...' },
  { name: 'Thesis.pdf', content: 'PhD Thesis\nTitle: AI and Society\n...' },
  { name: 'Schedule.ics', content: 'BEGIN:VCALENDAR\nSUMMARY:Team Meeting\n...' },
  { name: 'Notes.txt', content: 'Random notes\n- Buy milk\n- Call Alice' },
];

// allow multiple selection of file names
const selectedFiles = ref<string[]>([]);
// compute selected file objects
const selectedContents = computed(() => files.filter(f => selectedFiles.value.includes(f.name)));

// Emit the selected file content to parent on change
// emit whenever selection changes: send array of file objects
watch(selectedFiles, () => {
  emitFiles(selectedContents.value);
});

const emit = defineEmits(['update:contextFiles', 'close']);
function emitFiles(files: Array<{ name: string; content: string }>) {
  emit('update:contextFiles', files);
}
// Emit initial empty selection
emitFiles(selectedContents.value);
// handle click: ctrl/Cmd for multi-select
function onFileClick(event: MouseEvent, name: string) {
  if (event.ctrlKey || event.metaKey) {
    if (selectedFiles.value.includes(name)) {
      selectedFiles.value = selectedFiles.value.filter(n => n !== name);
    } else {
      // Use a new array for reactivity
      selectedFiles.value = [...selectedFiles.value, name];
    }
  } else {
    selectedFiles.value = [name];
  }
}
// icon mapping by extension
function fileIcon(name: string) {
  const ext = name.split('.').pop()?.toLowerCase();
  const map: Record<string, string> = { pdf: '📄', docx: '📄', txt: '📝' };
  return map[ext || ''] || '📁';
}

// Emit initial empty selection
emitFiles(selectedContents.value);
</script>

<style scoped>
/* Layout container */
.redesigned-context-provider {
  width: 340px;
  min-width: 240px;
  max-width: 360px;
  height: 520px;
  background: #fff;
  border-radius: 0.7rem;
  box-shadow: 0 0 24px 0 rgba(0,0,0,0.08);
  padding: 0.75rem 1rem 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  margin-top: 0;
}
.context-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.small-title {
  font-size: 1.05em;
  font-weight: 600;
}
.close-btn {
  padding: 0.1rem 0.5rem;
  font-size: 1.1em;
  line-height: 1;
}
.context-controls {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  margin-top: 0.2rem;
  flex: 1 1 auto;
  min-height: 0;
}
.file-list-container {
  width: 100%;
  flex: 0 0 auto;
  margin-bottom: 0.5rem;
}
.file-list {
  background: #252526;
  color: #ccc;
  border-radius: 4px;
  padding: 0.5rem 0.5rem 0.5rem 0.5rem;
  font-family: var(--bs-font-sans-serif);
  width: 100%;
  max-height: 120px;
  overflow-y: auto;
  box-sizing: border-box;
}
.file-item {
  display: flex;
  align-items: center;
  padding: 0.2rem 0.4rem;
  border-radius: 2px;
  cursor: pointer;
}
.file-item:hover {
  background: #373737;
}
.file-item.selected {
  background: #094771;
  color: #fff;
}
.file-icon {
  margin-right: 0.5rem;
}
.file-name {
  flex: 1;
}
.form-label-sm {
  font-size: 0.98em;
  margin-bottom: 0.2rem;
}
.context-content-container {
  flex: 1 1 0;
  min-height: 0;
  width: 100%;
  margin-bottom: 0.2rem;
  display: flex;
  flex-direction: column;
}
.context-content {
  font-size: 0.93em;
  background: #f8f9fa;
  border-radius: 0.4rem;
  padding: 0.5rem;
  width: 100%;
  flex: 1 1 0;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
  box-sizing: border-box;
}
.context-pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  font-family: inherit;
}
@media (max-width: 900px) {
  .redesigned-context-provider {
    width: 98vw;
    max-width: 100vw;
    height: 220px;
    border-radius: 0.5rem;
    padding: 0.5rem 0.5rem 0.3rem 0.5rem;
  }
  .context-content {
    max-height: 80px;
  }
}
@media (max-width: 600px) {
  .redesigned-context-provider {
    min-width: 100vw;
    max-width: 100vw;
    height: 160px;
    padding: 0.3rem 0.2rem 0.2rem 0.2rem;
  }
  .context-content {
    max-height: 50px;
  }
}
</style>
