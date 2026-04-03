// Team logo utility functions

const teamLogoMap: Record<string, string> = {
  "Hyderabad Kingsmen": "/logos/Hyderabad Kingsmen.png",
  "Islamabad United": "/logos/Islamabad United.png",
  "Karachi Kings": "/logos/Karachi Kings.png",
  "Lahore Qalandars": "/logos/Lahore Qalandars.png",
  "Multan Sultans": "/logos/Multan Sultan.png",
  "Multan Sultan": "/logos/Multan Sultan.png",
  "Peshawar Zalmi": "/logos/Peshawar Zalmi.png",
  "Quetta Gladiators": "/logos/Quetta Gladiators.png",
  "Rawalpindi PindiZ": "/logos/Rawalpindiz.png",
  "Rawalpindiz": "/logos/Rawalpindiz.png",
};

/**
 * Get the logo URL for a team name
 * Handles partial matches and variations
 */
export const getTeamLogo = (teamName: string): string => {
  if (!teamName) return "";
  
  // Exact match (case-insensitive)
  const exactMatch = Object.keys(teamLogoMap).find(
    key => key.toLowerCase() === teamName.toLowerCase()
  );
  if (exactMatch) {
    return teamLogoMap[exactMatch];
  }
  
  // Try to find a partial match
  const normalizedName = teamName.toLowerCase();
  for (const [key, value] of Object.entries(teamLogoMap)) {
    if (key.toLowerCase().includes(normalizedName) || normalizedName.includes(key.toLowerCase())) {
      return value;
    }
  }
  
  return "";
};

/**
 * Handle logo image errors with fallback
 */
export const handleLogoError = (e: React.SyntheticEvent<HTMLImageElement>) => {
  e.currentTarget.style.display = "none";
};

/**
 * Get all team names
 */
export const getAllTeams = (): string[] => {
  return Object.keys(teamLogoMap);
};
