"""
overcurrent.py - Overcurrent Protection Module
==============================================

This module monitors current and triggers actions when thresholds are exceeded.

Protection levels:
- NORMAL:   Current < WARNING threshold (normal operation)
- WARNING:  WARNING <= Current < CRITICAL (alert only)
- CRITICAL: Current >= CRITICAL threshold (trigger emergency stop)
"""

import time
from datetime import datetime

# ========================= CONFIGURATION =========================

# Default thresholds (for ACS712-20A)
DEFAULT_WARNING_THRESHOLD = 15.0     # Warning at 15A (75% of 20A range)
DEFAULT_CRITICAL_THRESHOLD = 18.0    # Critical at 18A (90% of 20A range)
DEFAULT_AUTO_SHUTDOWN = True         # Automatically trigger emergency stop
DEFAULT_ALERT_COOLDOWN = 30          # Seconds between repeated alerts

# Log file for overcurrent events
OVERCURRENT_LOG_FILE = "overcurrent_log.txt"


# ========================= CUSTOM EXCEPTION =========================

class OvercurrentError(Exception):
    """Custom exception for critical overcurrent conditions"""
    pass


# ========================= OVERCURRENT PROTECTION CLASS =========================

class OvercurrentProtection:
    """
    Monitors current and triggers actions when thresholds are exceeded.
    
    Usage:
        protection = OvercurrentProtection()
        
        # In your reading loop:
        alert_level = protection.check(current_amps)
        if alert_level == 'warning':
            # Send notification
            pass
        elif alert_level == 'critical':
            # Emergency shutdown
            pass
    """
    
    def __init__(self, 
                 warning_threshold=DEFAULT_WARNING_THRESHOLD,
                 critical_threshold=DEFAULT_CRITICAL_THRESHOLD,
                 auto_shutdown=DEFAULT_AUTO_SHUTDOWN,
                 alert_cooldown=DEFAULT_ALERT_COOLDOWN):
        """
        Initialize overcurrent protection system.
        
        Args:
            warning_threshold (float): Current in Amps for warning (default: 15.0)
            critical_threshold (float): Current in Amps for emergency (default: 18.0)
            auto_shutdown (bool): Whether to trigger emergency stop (default: True)
            alert_cooldown (int): Seconds between repeated alerts (default: 30)
        """
        self.warning = warning_threshold
        self.critical = critical_threshold
        self.auto_shutdown = auto_shutdown
        self.alert_cooldown = alert_cooldown
        
        # Internal state
        self.warning_count = 0
        self.critical_count = 0
        self.last_alert_time = None
        self._last_warning_time = None
        self._last_critical_time = None
    
    def check(self, current_a):
        """
        Check if current exceeds thresholds.
        
        Args:
            current_a (float): Measured current in Amps
            
        Returns:
            str: Status level ('normal', 'warning', 'critical')
            
        Raises:
            OvercurrentError: If critical threshold exceeded and auto_shutdown enabled
        """
        if current_a is None:
            return 'normal'
        
        abs_current = abs(current_a)
        
        # Check for critical overcurrent (highest priority)
        if abs_current >= self.critical:
            return self._handle_critical(abs_current)
        
        # Check for warning level
        elif abs_current >= self.warning:
            return self._handle_warning(abs_current)
        
        else:
            return 'normal'
    
    def _handle_warning(self, current):
        """Handle warning level overcurrent"""
        self.warning_count += 1
        now = datetime.now()
        
        # Check cooldown to avoid alert spam
        if (self._last_warning_time is None or 
            (now - self._last_warning_time).total_seconds() > self.alert_cooldown):
            
            self._log_alert('WARNING', current)
            self._send_warning_alert(current)
            self._last_warning_time = now
        
        return 'warning'
    
    def _handle_critical(self, current):
        """Handle critical level overcurrent"""
        self.critical_count += 1
        now = datetime.now()
        
        # Check cooldown to avoid spam
        if (self._last_critical_time is None or 
            (now - self._last_critical_time).total_seconds() > self.alert_cooldown):
            
            self._log_alert('CRITICAL', current)
            self._emergency_stop(current)
            self._last_critical_time = now
            
            # Raise exception if auto_shutdown is enabled
            if self.auto_shutdown:
                raise OvercurrentError(
                    f"CRITICAL overcurrent: {current:.2f}A >= {self.critical}A"
                )
        
        return 'critical'
    
    def _log_alert(self, level, current):
        """Log alert to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] {level}: {current:.2f}A"
        
        # Console output
        print(f"\n{'='*50}")
        if level == 'CRITICAL':
            print(f"🚨 {message} 🚨")
            print(f"   Emergency shutdown triggered!")
        else:
            print(f"⚠️  {message}")
            print(f"   Please reduce load.")
        print(f"{'='*50}\n")
        
        # Write to log file
        try:
            with open(OVERCURRENT_LOG_FILE, "a") as f:
                f.write(f"{message}\n")
        except IOError:
            print("⚠️ Could not write to log file")
    
    def _emergency_stop(self, current):
        """
        Execute emergency stop procedures.
        
        This function should be customized based on your hardware.
        """
        print("\n" + "🔴" * 20)
        print("EMERGENCY STOP EXECUTED")
        print(f"Current: {current:.2f}A exceeds {self.critical}A limit")
        print("🔴" * 20)
        
        # TODO: Add hardware-specific emergency actions below:
        # ============================================================
        
        # Option 1: Control a relay to cut power
        # import RPi.GPIO as GPIO
        # RELAY_PIN = 17
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(RELAY_PIN, GPIO.OUT)
        # GPIO.output(RELAY_PIN, GPIO.LOW)  # Cut power
        
        # Option 2: Turn on warning LED
        # LED_PIN = 27
        # GPIO.output(LED_PIN, GPIO.HIGH)
        
        # Option 3: Send signal to system to shutdown
        # import os
        # os.system("sudo shutdown -h now")
        
        # ============================================================
    
    def _send_warning_alert(self, current):
        """
        Send warning notification.
        
        Override this method to integrate with:
        - Email (SMTP)
        - Push notifications (Pushover, IFTTT)
        - Telegram bot
        - MQTT message
        """
        # TODO: Add your notification method here
        pass
    
    def get_stats(self):
        """Return protection system statistics"""
        return {
            'warning_count': self.warning_count,
            'critical_count': self.critical_count,
            'warning_threshold': self.warning,
            'critical_threshold': self.critical,
            'auto_shutdown': self.auto_shutdown
        }
    
    def reset_counts(self):
        """Reset warning and critical counters"""
        self.warning_count = 0
        self.critical_count = 0
        print("✓ Protection counters reset")
    
    def set_thresholds(self, warning=None, critical=None):
        """
        Dynamically change protection thresholds.
        
        Args:
            warning (float): New warning threshold in Amps
            critical (float): New critical threshold in Amps
        """
        if warning is not None:
            self.warning = warning
            print(f"✓ Warning threshold set to {warning} A")
        if critical is not None:
            self.critical = critical
            print(f"✓ Critical threshold set to {critical} A")
    
    def is_in_alarm(self):
        """Check if currently in alarm state"""
        return self.warning_count > 0 or self.critical_count > 0


# ========================= EMERGENCY STOP DECORATOR =========================

def emergency_stop_on_overcurrent(warning_threshold=15.0, critical_threshold=18.0):
    """
    Decorator that wraps a function with overcurrent protection.
    
    Usage:
        @emergency_stop_on_overcurrent(warning=10.0, critical=15.0)
        def read_sensor():
            return get_current_reading()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            protection = OvercurrentProtection(
                warning_threshold=warning_threshold,
                critical_threshold=critical_threshold
            )
            result = func(*args, **kwargs)
            
            # If the function returns a current value, check it
            if isinstance(result, (int, float)):
                protection.check(result)
            return result
        return wrapper
    return decorator


# ========================= TEST FUNCTIONS =========================

def test_overcurrent_protection():
    """Test the overcurrent protection system with simulated values"""
    print("\n🧪 Testing Overcurrent Protection System")
    print("="*50)
    
    protection = OvercurrentProtection(
        warning_threshold=1.0,
        critical_threshold=2.0,
        auto_shutdown=False  # Don't actually raise exceptions in test
    )
    
    test_currents = [0.5, 0.8, 1.2, 1.5, 2.2, 1.0]
    
    for current in test_currents:
        print(f"\nTesting {current}A:")
        try:
            level = protection.check(current)
            print(f"  Status: {level}")
        except OvercurrentError as e:
            print(f"  EXCEPTION: {e}")
    
    print("\n" + "="*50)
    print(f"Final stats: {protection.get_stats()}")


def simulate_overcurrent_scenario():
    """
    Simulate a realistic overcurrent scenario for testing.
    Run this to see how the protection system behaves.
    """
    print("\n🎬 Simulating overcurrent scenario")
    print("="*50)
    
    protection = OvercurrentProtection(
        warning_threshold=10.0,
        critical_threshold=15.0
    )
    
    # Simulate increasing current
    currents = [5.0, 8.0, 11.0, 12.5, 14.0, 16.0, 18.0]
    
    for i, current in enumerate(currents):
        print(f"\nStep {i+1}: {current}A")
        try:
            level = protection.check(current)
            time.sleep(0.5)
        except OvercurrentError as e:
            print(f"  🛑 {e}")
            break
    
    print("\n" + "="*50)
    print(f"Final stats: {protection.get_stats()}")


# ========================= MAIN (when run directly) =========================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_overcurrent_protection()
        elif sys.argv[1] == "--simulate":
            simulate_overcurrent_scenario()
        else:
            print("Usage: python overcurrent.py [--test | --simulate]")
    else:
        print("Overcurrent Protection Module")
        print("\nCommands:")
        print("  python overcurrent.py --test      - Run basic tests")
        print("  python overcurrent.py --simulate  - Run scenario simulation")
        print("\nImport in your code:")
        print("  from overcurrent import OvercurrentProtection, OvercurrentError")
        print("  protection = OvercurrentProtection()")
        print("  alert = protection.check(current_amps)")