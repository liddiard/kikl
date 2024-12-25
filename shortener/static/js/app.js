import { createApp } from 'vue'
import { generateWordPairings } from './utils.js'

import {
  getLinks,
  addLink,
  updateLinkDuration,
  deleteLink
} from './api.js'


const LinkStyled = {
  data() {
    return {
      href: '#',
    }
  },
  
  template: `
    <a :href="href" class="underline decoration-pink-500 decoration-1 underline-offset-2 hover:text-indigo-700 hover:decoration-2">
      <slot></slot>
    </a>`
}

createApp({
  async created() {
    this.links = await getLinks()
    // prevent input from getting defocused when links are rendered (not sure
    // why this happens)
    this.$refs.targetInput.focus()
  },

  data() {
    return {
      host: window.location.host,
      target: '',
      apiError: null,
      links: [],
      linkCopied: false,
    }
  },

  watch: {
    links: {
      handler: (newLinks) => {
        window.localStorage.setItem(
          'links',
          JSON.stringify(newLinks.map(l => l.uuid))
        )
      },
      deep: true
    }
  },
  
  methods: {
    async handleSubmit() {
      let link
      try {
        link = await addLink(this.target) 
      } catch (e) {
        this.apiError = e
        return
      }
      this.links.unshift(link)
      this.target = ''
    },

    async addTime(link) {
      let updatedLink
      try {
        updatedLink = await updateLinkDuration(link)
      } catch (e) {
        this.apiError = e
        return
      }
      this.links = this.links.map(l => l.uuid === link.uuid ? updatedLink : l)
    },

    async deleteLink(link) {
      if (!window.confirm(`⚠️ Are you sure you want to delete this link?\n\n${link.path} → ${link.target}`)) {
        return
      }
      let deletedLink
      try {
        deletedLink = await deleteLink(link)
      } catch (e) {
        this.apiError = e
        return
      }
      this.links = this.links.filter(l => l.uuid !== deletedLink.uuid)
    },

  /**
   * Calculates the number of hours remaining until a link expires.
   *
   * @param {Object} options - An object containing the duration and time_added of the link.
   * @param {number} options.duration - The duration of the link in hours.
   * @param {string} options.time_added - The time the link was added in ISO format.
   * @return {number} The number of hours remaining until the link expires (including decimals).
   */
    getLinkHoursRemaining({ duration, time_added }) {
      const linkEndTime = new Date(time_added)
      linkEndTime.setHours(linkEndTime.getHours() + duration)
      const msRemaining = linkEndTime - new Date()
      return msRemaining / 1000 / 60 / 60
    },

    /**
     * A function to pretty-print the expiration date and time of a link.
     *
     * @param {number} duration - The duration of the link in hours.
     * @param {string} time_added - The time the link was added in ISO format.
     * @return {string} The formatted expiration date and time.
     */
    getLinkExpiration({ duration, time_added }) {
      const linkExpiry = new Date(time_added)
      linkExpiry.setHours(linkExpiry.getHours() + duration)
      return Intl.DateTimeFormat('en-US', {
        weekday: 'long',
        hour: 'numeric',
        minute: 'numeric',
      }).format(linkExpiry)
    },

    /**
     * Checks if the duration of a link can be increased.
     *
     * @param {Object} link - The link object.
     * @return {boolean} Returns true if the duration of the link is less than the maximum duration (7 days), false otherwise.
     */
    canIncreaseLinkDuration(link) {
      return link.duration < (24 * 7)
    },

    copyLink(path) {
      this.linkCopied = false
      window.navigator.clipboard.writeText(`${window.location.origin}/${path}/`)
      this.linkCopied = true
    },

    handleLinkMouseout() {
      // in case the link was copied, we need to reset the "link copied" tooltip content
      // wait for the tooltip fade out animation to finish
      window.setTimeout(() => this.linkCopied = false, 250)
    }
  }
})
.component('link-styled', LinkStyled)
.mount('#app')

new Typewriter('#link-example', {
  strings: generateWordPairings(),
  pauseFor: 2000,
  autoStart: true,
  loop: true
});