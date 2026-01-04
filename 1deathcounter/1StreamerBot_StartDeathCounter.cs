// Streamer.bot Action: Start Death Counter Daemon
// Add this as a C# action in Streamer.bot
// This will launch the Python death counter daemon as a background process

using System;
using System.Diagnostics;
using System.IO;
using System.Threading;

public class CPHInline
{
    public bool Execute()
    {
        string scriptPath = @"C:\deathcounter\multi_game_death_counter.py";
        string baseDir = @"C:\deathcounter";
        string stopFile = Path.Combine(baseDir, "STOP");
        string lockFile = Path.Combine(baseDir, "daemon.lock");
        
        // Remove STOP file if it exists (in case previous instance didn't clean up)
        if (File.Exists(stopFile))
        {
            try
            {
                File.Delete(stopFile);
                CPH.LogInfo("Removed existing STOP file");
            }
            catch (Exception ex)
            {
                CPH.LogWarn($"Could not remove STOP file: {ex.Message}");
            }
        }
        
        // Check if daemon is already running
        if (File.Exists(lockFile))
        {
            CPH.LogWarn("Death counter daemon appears to be already running (lock file exists)");
            CPH.SendMessage("Death counter daemon is already running!");
            return true;
        }
        
        // Check if Python script exists
        if (!File.Exists(scriptPath))
        {
            CPH.LogError($"Python script not found at: {scriptPath}");
            CPH.SendMessage($"ERROR: Death counter script not found at {scriptPath}");
            return false;
        }
        
        try
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                UseShellExecute = false,
                CreateNoWindow = true, // Run in background
                WorkingDirectory = Path.GetDirectoryName(scriptPath)
            };
            
            Process.Start(psi);
            
            // Give it a moment to start
            Thread.Sleep(500);
            
            if (File.Exists(lockFile))
            {
                CPH.LogInfo("Death counter daemon started successfully");
                CPH.SendMessage("Death counter daemon started!");
            }
            else
            {
                CPH.LogWarn("Death counter daemon may have failed to start (no lock file)");
                CPH.SendMessage("Death counter daemon may have failed to start. Check logs.");
            }
        }
        catch (Exception ex)
        {
            CPH.LogError($"Failed to start death counter: {ex.Message}");
            CPH.SendMessage($"ERROR: Failed to start death counter: {ex.Message}");
            return false;
        }
        
        return true;
    }
}

