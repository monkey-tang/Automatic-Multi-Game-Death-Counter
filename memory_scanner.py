"""
Process Memory Scanning Module for Death Detection
Scans game process memory for death-related patterns using Windows ReadProcessMemory API.

Compatible with Windows 10/11.
No external dependencies required (uses ctypes for Windows API).
"""

import ctypes
import ctypes.wintypes
import time
import threading
from typing import Dict, List, Optional, Callable, Tuple
import struct

# Import psutil for process checking (optional - main daemon already imports it)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create dummy exception classes for compatibility
    class NoSuchProcess(Exception):
        pass
    class AccessDenied(Exception):
        pass
    psutil = type('psutil', (), {'NoSuchProcess': NoSuchProcess, 'AccessDenied': AccessDenied})()

# Windows API constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40

# Windows API structures
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
    ]


class MemoryScanner:
    """
    Scans game process memory for death-related patterns.
    Compatible with Windows 10/11 using ReadProcessMemory API.
    """
    
    def __init__(self, game_config: Dict, process: Optional[object] = None, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize memory scanner for a game configuration.
        
        Args:
            game_config: Game configuration dict with optional 'memory_scanning' section
            process: Optional psutil.Process object for the game process
            log_callback: Optional callback function for logging (for debugging)
        """
        self.game_config = game_config
        self.process = process
        self.log_callback = log_callback or (lambda msg: None)
        
        # Get memory scanning config
        self.config = game_config.get("memory_scanning", {})
        self.enabled = self.config.get("enabled", False)
        
        if not self.enabled:
            return
        
        # Get patterns
        self.patterns = self.config.get("patterns", [])
        self.scan_interval = self.config.get("scan_interval_seconds", 1.0)
        
        # Windows API functions
        self.kernel32 = ctypes.windll.kernel32
        # VirtualQueryEx is in kernel32.dll, not psapi.dll
        # psapi.dll is not needed for basic memory scanning
        
        # Process handle
        self.process_handle = None
        
        # Detection callback
        self.detection_callback = None
        
        # Scanning thread
        self.scan_thread = None
        self.stop_scanning = False
        self.lock = threading.Lock()
        
        # Cache for scanned addresses (to avoid re-scanning)
        self.scanned_regions = set()
        self.last_scan_time = 0
        
        # Setup VirtualQueryEx function signature (Windows 10/11 compatible)
        if self.kernel32:
            try:
                self.VirtualQueryEx = self.kernel32.VirtualQueryEx
                self.VirtualQueryEx.argtypes = [
                    ctypes.wintypes.HANDLE,
                    ctypes.c_void_p,
                    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                    ctypes.c_size_t
                ]
                self.VirtualQueryEx.restype = ctypes.c_size_t
            except Exception:
                self.VirtualQueryEx = None
        else:
            self.VirtualQueryEx = None
        
        if self.process and self.patterns:
            self._open_process()
    
    def _open_process(self):
        """Open process handle for memory reading."""
        if not self.process:
            return
        
        try:
            pid = self.process.pid
            # Try to open process with required permissions
            handle = self.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False,
                pid
            )
            
            if handle and handle != -1:
                self.process_handle = handle
                self.log_callback(f"MemoryScanner: Opened process handle for PID {pid}")
            else:
                error_code = self.kernel32.GetLastError()
                if error_code == 5:  # ACCESS_DENIED
                    self.log_callback(f"MemoryScanner: Access denied to process PID {pid} (may need admin rights)")
                else:
                    self.log_callback(f"MemoryScanner: Failed to open process PID {pid}, error code: {error_code}")
        except Exception as e:
            self.log_callback(f"MemoryScanner: Exception opening process: {e}")
    
    def _close_process(self):
        """Close process handle."""
        if self.process_handle:
            try:
                self.kernel32.CloseHandle(self.process_handle)
            except Exception:
                pass
            self.process_handle = None
    
    def _read_memory_region(self, address: int, size: int) -> Optional[bytes]:
        """Read memory region from process."""
        if not self.process_handle:
            return None
        
        try:
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t(0)
            
            success = self.kernel32.ReadProcessMemory(
                self.process_handle,
                ctypes.c_void_p(address),
                buffer,
                size,
                ctypes.byref(bytes_read)
            )
            
            if success and bytes_read.value > 0:
                return buffer.raw[:bytes_read.value]
        except Exception:
            pass
        
        return None
    
    def _get_memory_regions(self) -> List[Tuple[int, int]]:
        """Get readable memory regions from process."""
        regions = []
        
        if not self.process_handle or not self.VirtualQueryEx:
            return regions
        
        try:
            address = 0
            max_address = 0x7FFFFFFF  # 32-bit user space limit (for compatibility with Windows 10/11)
            max_iterations = 10000  # Safety limit to prevent infinite loops
            
            iteration = 0
            while address < max_address and iteration < max_iterations:
                iteration += 1
                
                mbi = MEMORY_BASIC_INFORMATION()
                size = ctypes.sizeof(mbi)
                
                result = self.VirtualQueryEx(
                    self.process_handle,
                    ctypes.c_void_p(address),
                    ctypes.byref(mbi),
                    size
                )
                
                if result == 0:
                    # No more regions or error
                    break
                
                # Extract address and size values (handle both int and ctypes value types)
                try:
                    if isinstance(mbi.BaseAddress, int):
                        base_addr = mbi.BaseAddress
                    else:
                        base_addr = mbi.BaseAddress.value if hasattr(mbi.BaseAddress, 'value') else int(mbi.BaseAddress)
                    
                    if isinstance(mbi.RegionSize, int):
                        region_size = mbi.RegionSize
                    else:
                        region_size = mbi.RegionSize.value if hasattr(mbi.RegionSize, 'value') else int(mbi.RegionSize)
                except (AttributeError, ValueError, TypeError):
                    # If we can't extract values, skip this region
                    break
                
                # Check if region is readable and committed
                if (mbi.State == MEM_COMMIT and
                    mbi.Protect in (PAGE_READONLY, PAGE_READWRITE, PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE)):
                    regions.append((base_addr, region_size))
                
                # Move to next region
                next_addr = base_addr + region_size
                
                if next_addr <= address:
                    # Prevent infinite loop if address doesn't advance
                    break
                
                address = next_addr
                
        except Exception:
            # Silently handle errors (access denied, invalid handle, etc.)
            pass
        
        return regions
    
    def _scan_memory_for_patterns(self) -> bool:
        """Scan memory for configured patterns. Returns True if pattern found."""
        if not self.process_handle or not self.patterns:
            return False
        
        try:
            # Get memory regions
            regions = self._get_memory_regions()
            
            # Limit scanning to reasonable number of regions to avoid performance issues
            max_regions = self.config.get("max_regions_per_scan", 100)
            regions = regions[:max_regions]
            
            # Scan each region
            for base_address, region_size in regions:
                if self.stop_scanning:
                    break
                
                # Limit region size to avoid huge reads
                max_region_size = self.config.get("max_region_size", 1024 * 1024)  # 1MB default
                scan_size = min(region_size, max_region_size)
                
                # Skip if we've scanned this region recently
                region_key = (base_address, scan_size)
                if region_key in self.scanned_regions:
                    continue
                
                # Read memory
                memory_data = self._read_memory_region(base_address, scan_size)
                if not memory_data:
                    continue
                
                # Check each pattern
                for pattern_config in self.patterns:
                    if self.stop_scanning:
                        break
                    
                    pattern_type = pattern_config.get("type", "string")
                    pattern_value = pattern_config.get("value")
                    
                    if pattern_type == "string":
                        # String pattern matching
                        encoding = pattern_config.get("encoding", "utf-8")
                        try:
                            pattern_bytes = pattern_value.encode(encoding)
                            if pattern_bytes in memory_data:
                                self.scanned_regions.add(region_key)
                                return True
                        except Exception:
                            pass
                    
                    elif pattern_type == "integer":
                        # Integer pattern matching
                        try:
                            value_size = pattern_config.get("size", 4)  # 4 bytes default
                            value = int(pattern_value)
                            
                            # Try different endianness
                            if value_size == 4:
                                pattern_bytes = struct.pack("<I", value)  # Little-endian
                                if pattern_bytes in memory_data:
                                    self.scanned_regions.add(region_key)
                                    return True
                                pattern_bytes = struct.pack(">I", value)  # Big-endian
                                if pattern_bytes in memory_data:
                                    self.scanned_regions.add(region_key)
                                    return True
                        except Exception:
                            pass
                
                # Mark region as scanned
                self.scanned_regions.add(region_key)
                
                # Limit number of cached regions
                if len(self.scanned_regions) > 1000:
                    self.scanned_regions.clear()
                
        except Exception:
            pass
        
        return False
    
    def _scan_loop(self):
        """Main scanning loop (runs in separate thread)."""
        while not self.stop_scanning:
            try:
                # Check if process is still running (with proper error handling)
                try:
                    if not self.process:
                        break
                    if PSUTIL_AVAILABLE and hasattr(self.process, 'is_running'):
                        # psutil.Process has is_running method
                        if not self.process.is_running():
                            self.log_callback("MemoryScanner: Process no longer running")
                            break
                    elif PSUTIL_AVAILABLE and hasattr(psutil, 'pid_exists'):
                        # Try psutil.pid_exists as fallback
                        try:
                            if hasattr(self.process, 'pid'):
                                if not psutil.pid_exists(self.process.pid):
                                    self.log_callback("MemoryScanner: Process no longer running (PID not found)")
                                    break
                        except Exception:
                            pass
                    # If psutil not available, continue scanning (assume process is still running)
                except Exception as e:
                    # Handle psutil exceptions gracefully
                    if PSUTIL_AVAILABLE:
                        if isinstance(e, (psutil.NoSuchProcess, psutil.AccessDenied)):
                            self.log_callback("MemoryScanner: Process check failed, stopping scan")
                            break
                    # For other errors, log and continue
                    try:
                        self.log_callback(f"MemoryScanner: Process check error: {e}")
                    except:
                        pass
                
                # Check if process handle is valid
                if not self.process_handle:
                    with self.lock:
                        self._open_process()
                    if not self.process_handle:
                        time.sleep(self.scan_interval)
                        continue
                
                # Scan memory
                if self._scan_memory_for_patterns():
                    if self.detection_callback:
                        try:
                            self.detection_callback()
                        except Exception:
                            pass
                
                # Clear cache periodically to allow re-scanning
                if len(self.scanned_regions) > 500:
                    self.scanned_regions.clear()
                
            except Exception as e:
                # Log unexpected errors but continue
                try:
                    self.log_callback(f"MemoryScanner: Scan loop error: {e}")
                except:
                    pass
            
            time.sleep(self.scan_interval)
    
    def set_detection_callback(self, callback: Callable[[], None]):
        """
        Set callback function to call when death is detected.
        
        Args:
            callback: Function to call (no arguments)
        """
        self.detection_callback = callback
    
    def start(self, process: Optional[object] = None):
        """
        Start memory scanning.
        
        Args:
            process: Optional psutil.Process object (updates if provided)
        """
        with self.lock:
            if not self.enabled or not self.patterns:
                return
            
            if process:
                self.process = process
            
            if not self.process:
                return
            
            # Don't start if already running
            if self.scan_thread and self.scan_thread.is_alive():
                return
            
            # Open process if needed
            if not self.process_handle:
                self._open_process()
            
            if not self.process_handle:
                return
            
            # Start scanning thread
            self.stop_scanning = False
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()
            self.log_callback("MemoryScanner: Started scanning thread")
    
    def stop(self):
        """Stop memory scanning."""
        with self.lock:
            self.stop_scanning = True
            
            if self.scan_thread and self.scan_thread.is_alive():
                # Wait for thread to stop
                time.sleep(0.5)
            
            self._close_process()
            self.scanned_regions.clear()
            self.detection_callback = None
    
    def is_enabled(self) -> bool:
        """Check if scanning is enabled."""
        return self.enabled and bool(self.patterns)
    
    def update_process(self, process: Optional[object]):
        """Update target process (e.g., when game switches)."""
        # Check if actually changing (compare PIDs if both are psutil.Process objects)
        try:
            if self.process and process:
                if hasattr(self.process, 'pid') and hasattr(process, 'pid'):
                    if self.process.pid == process.pid:
                        return  # Same process, no change needed
            elif self.process is None and process is None:
                return  # Both None, no change needed
        except Exception:
            # If comparison fails, assume we need to update
            pass
        
        was_running = False
        with self.lock:
            was_running = self.scan_thread and self.scan_thread.is_alive()
        
        # Stop outside lock to avoid deadlock (stop() uses lock internally)
        self.stop()
        
        # Update process and restart if needed
        self.process = process
        
        if was_running and self.enabled and process:
            # Close old handle if exists
            self._close_process()
            
            # Open new process handle
            self._open_process()
            
            # Restart scanning thread if we have a valid handle
            if self.process_handle:
                with self.lock:
                    if not (self.scan_thread and self.scan_thread.is_alive()):
                        self.stop_scanning = False
                        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
                        self.scan_thread.start()
                        self.log_callback("MemoryScanner: Restarted scanning thread with new process")
    
    def update_config(self, game_config: Dict, process: Optional[object] = None):
        """
        Update configuration when game switches.
        Stops current scanning and restarts with new config.
        """
        self.stop()
        self.game_config = game_config
        self.config = game_config.get("memory_scanning", {})
        self.enabled = self.config.get("enabled", False)
        
        if process:
            self.process = process
        
        if self.enabled:
            self.patterns = self.config.get("patterns", [])
            self.scan_interval = self.config.get("scan_interval_seconds", 1.0)
            self.scanned_regions = set()
            
            if self.process and self.patterns:
                self.start()
