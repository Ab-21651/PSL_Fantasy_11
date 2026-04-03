/**
 * Get the player image URL from the player name
 * Images are stored in /players/ folder with format "Player Name.jpg"
 */
export function getPlayerImageUrl(playerName: string): string {
  if (!playerName) return '/players/default.jpg';
  // Use player name as is (photos are named exactly as player names)
  return `/players/${playerName}.jpg`;
}

/**
 * Handle image load errors with fallback
 */
export function handleImageError(e: React.SyntheticEvent<HTMLImageElement>) {
  const img = e.currentTarget;
  // Set a fallback background color or icon
  img.style.display = 'none';
  if (img.parentElement) {
    img.parentElement.classList.add('bg-gradient-to-br', 'from-primary/20', 'to-accent/20');
  }
}
