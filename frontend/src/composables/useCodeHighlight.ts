import { nextTick } from 'vue';
import hljs from 'highlight.js';

/**
 * Provides utilities to highlight code blocks and add copy buttons in chat history.
 */
export function useCodeHighlight() {
  const addCopyButtonsToCodeBlocks = () => {
    document.querySelectorAll('.chat-history pre code').forEach((block) => {
      const pre = block.parentElement;
      if (!pre) return;
      if (pre.querySelector('.copy-btn')) return;
      const btn = document.createElement('button');
      btn.className = 'copy-btn btn btn-sm btn-light position-absolute top-0 end-0 m-2';
      btn.textContent = 'Copy';
      btn.style.zIndex = '2';
      btn.setAttribute('type', 'button');
      btn.onclick = async (e) => {
        e.stopPropagation();
        try {
          await navigator.clipboard.writeText(block.textContent || '');
          btn.textContent = 'Copied!';
          btn.setAttribute('data-copied', 'true');
          setTimeout(() => {
            btn.textContent = 'Copy';
            btn.removeAttribute('data-copied');
          }, 1200);
        } catch {
          btn.textContent = 'Error';
        }
      };
      pre.style.position = 'relative';
      pre.appendChild(btn);
    });
  };

  const highlightAllCode = () => {
    nextTick(() => {
      document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block as HTMLElement);
      });
      addCopyButtonsToCodeBlocks();
    });
  };

  return { highlightAllCode };
}
