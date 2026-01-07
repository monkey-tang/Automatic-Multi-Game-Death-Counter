// Streamer.bot Action: Switch Game and Get Death Count
// This action switches to a game AND gets the current death count
// Usage: Set a Streamer.bot argument "GameName" or Global Variable "GameName"

using System;
using System.IO;
using Newtonsoft.Json.Linq;

public class CPHInline
{
    public bool Execute()
    {
        string configFile = @"C:\deathcounter\games_config.json";
        string stateFile = @"C:\deathcounter\death_state.json";
        string deathTxt = @"C:\deathcounter\death_counter.txt";
        
        // Get game name from Streamer.bot arguments or variables
        string gameName = CPH.GetGlobalVar<string>("GameName", false);
        if (string.IsNullOrEmpty(gameName))
        {
            gameName = CPH.ArgsAsDict().ContainsKey("GameName") 
                ? CPH.ArgsAsDict()["GameName"].ToString() 
                : null;
        }
        
        // If no game name provided, just get death count without switching
        if (!string.IsNullOrEmpty(gameName))
        {
            // Switch game first
            if (!File.Exists(configFile))
            {
                CPH.LogError($"Config file not found: {configFile}");
                CPH.SendMessage($"ERROR: Config file not found. Run the daemon first to create it.");
                return false;
            }
            
            try
            {
                string jsonContent = File.ReadAllText(configFile);
                JObject config = JObject.Parse(jsonContent);
                
                JObject games = config["games"] as JObject;
                if (games == null || !games.ContainsKey(gameName))
                {
                    CPH.LogError($"Game '{gameName}' not found in configuration.");
                    CPH.SendMessage($"ERROR: Game '{gameName}' not found in config.");
                    
                    if (games != null)
                    {
                        string availableGames = string.Join(", ", games.Properties().Select(p => p.Name));
                        CPH.SendMessage($"Available games: {availableGames}");
                    }
                    return false;
                }
                
                // Update current game
                config["current_game"] = gameName;
                
                // Save config
                File.WriteAllText(configFile, config.ToString(Newtonsoft.Json.Formatting.Indented));
                
                CPH.LogInfo($"Switched death counter to game: {gameName}");
                
                // Update global variable
                CPH.SetGlobalVar("DeathCounterCurrentGame", gameName, false);
            }
            catch (Exception ex)
            {
                CPH.LogError($"Error switching game: {ex.Message}");
                CPH.SendMessage($"ERROR: Failed to switch game: {ex.Message}");
                return false;
            }
        }
        
        // Get death count (regardless of whether we switched games)
        int totalDeaths = 0;
        string currentGame = "Unknown";
        int gameDeaths = 0;
        
        try
        {
            // Try to read from JSON state file first (more detailed)
            if (File.Exists(stateFile))
            {
                string jsonContent = File.ReadAllText(stateFile);
                JObject state = JObject.Parse(jsonContent);
                
                totalDeaths = state["total_deaths"]?.Value<int>() ?? 0;
                currentGame = state["current_game"]?.Value<string>() ?? gameName ?? "Unknown";
                
                if (currentGame != "Unknown" && state["game_deaths"] != null)
                {
                    gameDeaths = state["game_deaths"][currentGame]?.Value<int>() ?? 0;
                }
            }
            // Fallback to text file
            else if (File.Exists(deathTxt))
            {
                string content = File.ReadAllText(deathTxt).Trim();
                if (int.TryParse(content, out totalDeaths))
                {
                    // Successfully parsed from text file
                }
            }
        }
        catch (Exception ex)
        {
            CPH.LogError($"Error reading death count: {ex.Message}");
            CPH.SendMessage($"ERROR: Could not read death count: {ex.Message}");
            return false;
        }
        
        // Set Streamer.bot variables
        CPH.SetGlobalVar("DeathCountTotal", totalDeaths, false);
        CPH.SetGlobalVar("DeathCountGame", gameDeaths, false);
        CPH.SetGlobalVar("DeathCounterCurrentGame", currentGame, false);
        
        // Log the values
        CPH.LogInfo($"Death Count - Total: {totalDeaths}, {currentGame}: {gameDeaths}");
        
        return true;
    }
}





