// Streamer.bot Action: Stop Death Counter Daemon
// Add this as a C# action in Streamer.bot
// This will gracefully stop the Python death counter daemon

using System;
using System.IO;
using System.Threading;

public class CPHInline
{
    public bool Execute()
    {
        string baseDir = @"C:\deathcounter";
        string stopFile = Path.Combine(baseDir, "STOP");
        string lockFile = Path.Combine(baseDir, "daemon.lock");
        
        // Check if daemon is running
        if (!File.Exists(lockFile))
        {
            CPH.LogInfo("Death counter daemon is not running (no lock file)");
            CPH.SendMessage("Death counter daemon is not running.");
            return true;
        }
        
        try
        {
            // Create STOP file to signal daemon to exit gracefully
            Directory.CreateDirectory(baseDir);
            File.Create(stopFile).Close();
            
            CPH.LogInfo("STOP file created. Waiting for daemon to exit...");
            CPH.SendMessage("Stopping death counter daemon...");
            
            // Wait up to 5 seconds for daemon to stop
            for (int i = 0; i < 50; i++)
            {
                Thread.Sleep(100);
                if (!File.Exists(lockFile))
                {
                    CPH.LogInfo("Death counter daemon stopped successfully");
                    CPH.SendMessage("Death counter daemon stopped!");
                    
                    // Clean up STOP file
                    if (File.Exists(stopFile))
                    {
                        try { File.Delete(stopFile); } catch { }
                    }
                    return true;
                }
            }
            
            // If lock file still exists after 5 seconds, daemon may have crashed
            if (File.Exists(lockFile))
            {
                CPH.LogWarn("Daemon did not stop within timeout. Lock file still exists.");
                CPH.SendMessage("Warning: Daemon may not have stopped. Check manually.");
            }
        }
        catch (Exception ex)
        {
            CPH.LogError($"Error stopping death counter: {ex.Message}");
            CPH.SendMessage($"ERROR: Failed to stop death counter: {ex.Message}");
            return false;
        }
        
        return true;
    }
}

