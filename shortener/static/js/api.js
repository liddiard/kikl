// CSRF token populated by Django template
const { CSRF_TOKEN } = window

const MAX_ACTIVE_LINKS = 10

/**
 * Retrieves and parses UUIDs from local storage, handling potential errors.
 *
 * @return {Array} Array of UUIDs retrieved from local storage
 */
function getLinkUuids() {
  let uuids
  try {
    // slice to ensure we don't exceed MAX_ACTIVE_LINKS (can happen if a link
    // expired while the page was open)
    uuids = (JSON.parse(window.localStorage.getItem('links')) ?? []).slice(0, MAX_ACTIVE_LINKS)
  } catch (e) {
    uuids = []
  }
  return uuids
}

/**
 * Retrieves links from the server based on the UUIDs stored in local storage.
 *
 * @return {Array} An array of links retrieved from the server
 */
export async function getLinks() {
  const uuids = getLinkUuids()
  if (!uuids.length) {
    return []
  }
  const response = await fetch(`/api/link/?uuids=${uuids.join(',')}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN
    }
  })
  const json = await response.json()
  if (!response.ok) {
    throw new Error(json.error)
  }
  return json?.links ?? []
}

/**
 * Sends a POST request to add a new link to the server.
 *
 * @param {string} target - The target link to be added
 * @return {Promise} A promise that resolves with the newly created link object from the server
 */
export async function addLink(target) {
  const response = await fetch('/api/link/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN
    },
    body: JSON.stringify({ target })
  })
  const json = await response.json()
  if (!response.ok) {
    throw new Error(json.error)
  }
  return json
}

/**
 * Updates the duration of a link by sending a PATCH request to the server.
 *
 * @param {Object} link - The link object to update with a new duration
 * @param {number} [timeToAdd=24] - The time to add to the current duration in hours
 * @return {Promise} A promise that resolves with the updated link object from the server
 */
export async function updateLinkDuration(link, timeToAdd = 24) { // hours
  const { uuid } = link
  const response = await fetch('/api/link/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN
    },
    body: JSON.stringify({
      uuid,
      duration: link.duration + timeToAdd
    })
  })
  const json = await response.json()
  if (!response.ok) {
    throw new Error(json.error)
  }
  return json
}

/**
 * Deletes a link by sending a DELETE request to the server.
 *
 * @param {Object} link - The link object to delete
 * @return {Promise} A promise that resolves to an object with the deleted link's UUID
 */
export async function deleteLink(link) {
  const { uuid } = link
  const response = await fetch('/api/link/', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN
    },
    body: JSON.stringify({ uuid })
  })
  const json = await response.json()
  if (!response.ok) {
    throw new Error(json.error)
  }
  return json
}