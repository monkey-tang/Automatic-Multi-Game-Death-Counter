// Streamer.bot Action: Switch Death Counter Game
// Add this as a C# action in Streamer.bot
// Usage: Set a Streamer.bot argument "GameName" to the game you want to switch to
// Example: Create a Streamer.bot action with argument "GameName" = "Elden Ring"

using System;
using System.IO;
using Newtonsoft.Json.Linq;

public class CPHInline
{
    public bool Execute()
    {
        string configFile = @"C:\deathcounter\games_config.json";
        
        // Get game name from Streamer.bot arguments (or use default)
        string gameName = CPH.GetGlobalVar<string>("GameName", false);
        if (string.IsNullOrEmpty(gameName))
        {
            // Try to get from action arguments if available
            gameName = CPH.ArgsAsDict().ContainsKey("GameName") 
                ? CPH.ArgsAsDict()["GameName"].ToString() 
                : null;
        }
        
        if (string.IsNullOrEmpty(gameName))
        {
            CPH.LogError("No game name provided. Set 'GameName' variable or argument.");
            CPH.SendMessage("ERROR: No game name provided for switching.");
            return false;
        }
        
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
                
                // List available games
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
            CPH.SendMessage($"Switched death counter to: {gameName}");
            
            // Update global variable
            CPH.SetGlobalVar("DeathCounterCurrentGame", gameName, false);
            
            return true;
        }
        catch (Exception ex)
        {
            CPH.LogError($"Error switching game: {ex.Message}");
            CPH.SendMessage($"ERROR: Failed to switch game: {ex.Message}");
            return false;
        }
    }
}

