import { adjectives, nouns } from './words.js'

// https://stackoverflow.com/a/12646864/2487925
const shuffle = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}

export const generateWordPairings = () => {
  shuffle(nouns)
  shuffle(adjectives)
  return adjectives
  .map((adj, i) => `${adj}-${nouns[i]}`)
}