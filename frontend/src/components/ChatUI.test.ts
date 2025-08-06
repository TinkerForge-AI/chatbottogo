import { mount } from '@vue/test-utils'
import ChatUI from './ChatUI.vue'
import { describe, it, expect } from 'vitest'

describe('ChatUI', () => {
  it('renders input and send button', () => {
    const wrapper = mount(ChatUI)
    expect(wrapper.find('input[aria-label="Type your message"]').exists()).toBe(true)
    expect(wrapper.find('button[aria-label="Send message"]').exists()).toBe(true)
  })

  it('displays user and bot messages', async () => {
    const wrapper = mount(ChatUI)
    // Simulate user input
    await wrapper.find('input').setValue('Hello!')
    await wrapper.find('form').trigger('submit.prevent')
    // Wait for streaming
    await new Promise(r => setTimeout(r, 1800))
    expect(wrapper.text()).toContain('You')
    expect(wrapper.text()).toContain('Bot')
  })

  it('shows typing indicator when streaming', async () => {
    const wrapper = mount(ChatUI)
    await wrapper.find('input').setValue('Test')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('Bot is typing')
  })

  it('has accessible ARIA labels', () => {
    const wrapper = mount(ChatUI)
    expect(wrapper.find('input[aria-label="Type your message"]').exists()).toBe(true)
    expect(wrapper.find('button[aria-label="Send message"]').exists()).toBe(true)
    expect(wrapper.find('select[aria-label="Query type"]').exists()).toBe(true)
  })
})
