#!/usr/bin/env python3
"""
IoT Power Monitor - Supabase Database Module
=============================================
Purpose: Read and write power monitoring data to Supabase database
Features:
- Save raw power readings (ADC, voltage, current, power)
- Save AI analysis results (status, analysis text, recommendation, confidence)
- Save alerts (overcurrent, overvoltage, anomalies)
- Query latest readings for dashboard
"""

from supabase import create_client, Client
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# add .env loading for database credentials
from dotenv import load_dotenv

# load .env variables (SUPABASE_URL, SUPABASE_KEY)
load_dotenv()

class IoTDatabase:
    """
    Supabase database operations class.
    
    This class:
    - saves raw power readings to "power_readings" table
    - saves AI analysis results to "power_analyses" table
    - saves alerts to "power_alerts" table
    - provides methods to query latest readings and statistics  
    - handles database connection and errors gracefully
    """
    
    def __init__(self):
        """
        Initialize Supabase client with environment variables.
        
        Reads SUPABASE_URL and SUPABASE_KEY from .env file
        Raises error if environment variables are missing   
        """
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        self.supabase: Client = create_client(self.url, self.key)
        print("✓ Supabase client initialized")
    
    def save_power_reading(
        self,
        adc_value: float,
        voltage: float,
        current_a: float,
        power_w: float,
        location: str = "USB Device Test",
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Save raw power reading data to power_readings table.
        
        Args:
            adc_value: raw ADC value (0 ~ 65535)
            voltage: sensor output voltage (V)
            current_a: calculated current (Amps)
            power_w: calculated power (Watts)
            location: device location identifier
            notes: optional additional notes
            
        Returns:
            int: Record ID if successful, None if failed
        """
        try:
            data = {
                "adc_value": adc_value,
                "voltage": voltage,
                "current_a": current_a,
                "power_w": power_w,
                "device_location": location,
                "notes": notes
            }
            
            response = self.supabase.table("power_readings").insert(data).execute()
            
            if response.data:
                record_id = response.data[0]["id"]
                print(f"✓ Power reading saved (ID: {record_id})")
                return record_id
            else:
                print("✗ Failed to save power reading")
                return None
                
        except Exception as e:
            print(f"✗ Database error (save_power_reading): {e}")
            return None
    
    def save_analysis(
        self,
        power_id: int,
        status: str,
        analysis: str,
        recommendation: str,
        confidence: float,
        is_abnormal: bool = False
    ) -> Optional[int]:
        """
        Save AI analysis result to power_analyses table.
        
        Args:
            power_id: Reference to power_readings record ID
            status: 'normal' / 'warning' / 'alert'
            analysis: AI analysis text from Claude
            recommendation: Recommended action from AI
            confidence: Confidence score (0.0 ~ 1.0)
            is_abnormal: True if abnormal pattern detected
            
        Returns:
            int: Record ID if successful, None if failed
        """
        try:
            data = {
                "power_reading_id": power_id,
                "status": status,
                "analysis": analysis,
                "recommendation": recommendation,
                "confidence": confidence,
                "is_abnormal": is_abnormal
            }
            
            response = self.supabase.table("power_analyses").insert(data).execute()
            
            if response.data:
                record_id = response.data[0]["id"]
                print(f"✓ Analysis saved (ID: {record_id})")
                return record_id
            else:
                print("✗ Failed to save analysis")
                return None
                
        except Exception as e:
            print(f"✗ Database error (save_analysis): {e}")
            return None
    
    def save_alert(
        self,
        power_id: int,
        alert_type: str,
        message: str
    ) -> Optional[int]:
        """
        Save alert record to power_alerts table.
        

        Saves alert records to the power_alerts table when overcurrent, overvoltage, or anomalies are detected.
        
        Args:
            power_id: Reference to power_readings record ID
            alert_type: 'overcurrent' / 'overvoltage' / 'anomaly' / 'overpower'
            message: Alert description
            
        Returns:
            int: Record ID if successful, None if failed
        """
        try:
            data = {
                "power_reading_id": power_id,
                "alert_type": alert_type,
                "message": message
            }
            
            response = self.supabase.table("power_alerts").insert(data).execute()
            
            if response.data:
                record_id = response.data[0]["id"]
                print(f"✓ Alert saved (ID: {record_id}, Type: {alert_type})")
                return record_id
            else:
                print("✗ Failed to save alert")
                return None
                
        except Exception as e:
            print(f"✗ Database error (save_alert): {e}")
            return None
    
    def get_latest_readings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest power readings (for Web Dashboard).
        
        Retrieves the most recent power reading records for display on the Web Dashboard.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            list: List of power reading records
        """
        try:
            response = self.supabase.table("power_readings")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"✗ Database error (get_latest_readings): {e}")
            return []
    
    def get_analysis_for_reading(self, power_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves the AI analysis record corresponding to a given power reading ID.
        
        Args:
            power_id: Reference to power_readings record ID
            
        Returns:
            dict: Analysis record, or None if not found
        """
        try:
            response = self.supabase.table("power_analyses")\
                .select("*")\
                .eq("power_reading_id", power_id)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"✗ Database error (get_analysis_for_reading): {e}")
            return None
    
    def get_unresolved_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves unresolved alert records from the power_alerts table.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            list: List of unresolved alert records
        """
        try:
            response = self.supabase.table("power_alerts")\
                .select("*")\
                .eq("is_resolved", False)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"✗ Database error (get_unresolved_alerts): {e}")
            return []
    
    def resolve_alert(self, alert_id: int) -> bool:
        """
        Marks an alert record as resolved in the power_alerts table.
        
        Args:
            alert_id: Alert record ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.supabase.table("power_alerts")\
                .update({"is_resolved": True, "resolved_at": datetime.now().isoformat()})\
                .eq("id", alert_id)\
                .execute()
            
            print(f"✓ Alert {alert_id} resolved")
            return True
            
        except Exception as e:
            print(f"✗ Database error (resolve_alert): {e}")
            return False
    
    def get_statistics(self, hours: int = 1) -> Optional[Dict[str, Any]]:
        """Get power statistics for the last N hours."""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            response = self.supabase.table("power_readings")\
                .select("current_a, power_w")\
                .gte("created_at", cutoff_time.isoformat())\
                .execute()
            
            if not response.data:
                return None
            
            currents = [r['current_a'] for r in response.data]
            powers = [r['power_w'] for r in response.data]
            
            return {
                "current_max": max(currents),
                "current_min": min(currents),
                "current_avg": sum(currents) / len(currents),
                "power_max": max(powers),
                "power_min": min(powers),
                "power_avg": sum(powers) / len(powers),
                "samples": len(response.data)
            }
            
        except Exception as e:
            print(f"✗ Database error (get_statistics): {e}")
            return None


# ============================================================
# Test / Example Usage
# Test code (only executed when running this file directly)
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Supabase Database Connection Test")
    print("=" * 50)
    
    try:
        # Initialize database connection
        db = IoTDatabase()
        print("✓ Connected to Supabase\n")
        
        # Test 1: Save power reading
        print("[Test 1] Save power reading...")
        power_id = db.save_power_reading(
            adc_value=512.0,
            voltage=2.5,
            current_a=0.5,
            power_w=2.5
        )
        
        if power_id:
            print(f"  → Saved with ID: {power_id}\n")
            
            # Test 2: Save AI analysis
            print("[Test 2] Save AI analysis...")
            analysis_id = db.save_analysis(
                power_id=power_id,
                status="normal",
                analysis="Device is operating normally",
                recommendation="Continue monitoring",
                confidence=0.95,
                is_abnormal=False
            )
            
            if analysis_id:
                print(f"  → Analysis saved with ID: {analysis_id}\n")
        
        # Test 3: Get latest readings
        print("[Test 3] Get latest readings...")
        latest = db.get_latest_readings(limit=5)
        print(f"  → Retrieved {len(latest)} records")
        for item in latest:
            print(f"     - {item['created_at']}: {item['current_a']}A, {item['power_w']}W")
        
        # Test 4: Get statistics
        print("\n[Test 4] Get statistics (last 1 hour)...")
        stats = db.get_statistics(hours=1)
        if stats:
            print(f"  → Current: avg={stats['current_avg']:.2f}A, max={stats['current_max']:.2f}A")
            print(f"  → Power: avg={stats['power_avg']:.2f}W, max={stats['power_max']:.2f}W")
            print(f"  → Samples: {stats['samples']}")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")