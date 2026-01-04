// Streamer.bot Action: Get Current Death Count
// Add this as a C# action in Streamer.bot
// Returns the current death count (can be used in messages, variables, etc.)

using System;
using System.IO;
using Newtonsoft.Json.Linq;

public class CPHInline
{
    public bool Execute()
    {
        string stateFile = @"C:\deathcounter\death_state.json";
        string deathTxt = @"C:\deathcounter\death_counter.txt";
        
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
                currentGame = state["current_game"]?.Value<string>() ?? "Unknown";
                
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

