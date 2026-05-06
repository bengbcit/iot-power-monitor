"""
IoT Power Monitor - LLM Analysis Module
Supports Groq, DeepSeek, Google, NVIDIA API providers
"""

import os
import re
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI


class LLMClient:
    """LLM Client supporting multiple providers (Groq, DeepSeek, Google, NVIDIA)"""
    
    def __init__(self, provider: str = "groq", model: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: "groq", "deepseek", "google", "nvidia"
            model: Model name (optional)
            api_key: API key (optional, reads from env if not provided)
        """
        self.provider = provider
        
        # Provider configurations
        configs = {
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "env_key": "GROQ_API_KEY",
                "default_model": "llama-3.3-70b-versatile",
            },
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "env_key": "DEEPSEEK_API_KEY",
                "default_model": "deepseek-chat",
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "env_key": "GOOGLE_API_KEY",
                "default_model": "gemini-2.0-flash",
            },
            "nvidia": {
                "base_url": "https://integrate.api.nvidia.com/v1",
                "env_key": "NVIDIA_API_KEY",
                "default_model": "meta/llama-3.3-70b-instruct",
            }
        }
        
        if provider not in configs:
            raise ValueError(f"Unknown provider: {provider}. Choose from: {list(configs.keys())}")
        
        config = configs[provider]
        
        # Get API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get(config["env_key"])
        
        if not self.api_key:
            raise ValueError(
                f"Missing API key for {provider}. "
                f"Set {config['env_key']} in .env file"
            )
        
        self.model = model or config["default_model"]
        
        # Initialize OpenAI-compatible client
        self.client = OpenAI(
            base_url=config["base_url"],
            api_key=self.api_key
        )
        
        print(f"[INIT] LLM client: {provider.upper()} | Model: {self.model}")
    
    def analyze_power_data(self, current_a: float, power_w: float, voltage_v: float = 5.0) -> Dict[str, Any]:
        """
        Analyze power consumption with safety rules
        
        Args:
            current_a: Current in Amperes
            power_w: Power in Watts
            voltage_v: Voltage in Volts (default 5.0)
        
        Returns:
            Dict with analysis results: status, analysis, recommendation, is_abnormal, confidence
        """
        
        # SAFETY FIRST: Check dangerous conditions immediately (no API call needed)
        if current_a > 3.0:
            return {
                "status": "alert",
                "analysis": f"CRITICAL: Overcurrent at {current_a}A exceeds 3.0A safety limit!",
                "recommendation": "IMMEDIATELY DISCONNECT POWER and check for short circuit!",
                "is_abnormal": True,
                "confidence": 0.99,
                "timestamp": datetime.now().isoformat()
            }
        elif current_a > 2.5:
            return {
                "status": "alert",
                "analysis": f"DANGER: Current {current_a}A exceeds 2.5A maximum safe current!",
                "recommendation": "Reduce load immediately or check for faulty components.",
                "is_abnormal": True,
                "confidence": 0.98,
                "timestamp": datetime.now().isoformat()
            }
        
        # Build system prompt with clear rules for 5V USB system
        system_prompt = """You are an IoT power monitor for a 5V USB system (Raspberry Pi, Arduino, USB devices).

STRICT RULES for 5V system:
- Current < 0.1A: status "normal" (standby/disconnected)
- Current 0.1A - 1.5A: status "normal" (normal operation)
- Current 1.5A - 2.5A: status "warning" (high power, monitor closely)
- Current > 2.5A: status "alert" (OVERLOAD - emergency)

Power rules (for 5V system):
- Power < 0.5W: normal
- Power 0.5W - 7.5W: normal
- Power 7.5W - 12.5W: warning
- Power > 12.5W: alert

Return ONLY valid JSON. No other text. Example:
{"status": "normal", "analysis": "Device operating normally at 1.0A", "recommendation": "No action needed", "is_abnormal": false, "confidence": 0.95}"""
        
        user_prompt = f"""Current reading:
- Current: {current_a} Amperes
- Power: {power_w} Watts
- Voltage: {voltage_v} Volts
- Time: {datetime.now().strftime('%H:%M:%S')}

Apply the 5V USB system rules and return JSON analysis."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "status": result.get("status", "normal"),
                    "analysis": result.get("analysis", "Monitoring in progress"),
                    "recommendation": result.get("recommendation", "Continue monitoring"),
                    "is_abnormal": result.get("is_abnormal", False),
                    "confidence": min(1.0, max(0.0, result.get("confidence", 0.5))),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"   [WARN] API error: {e}")
        
        # Fallback for non-dangerous cases when API fails
        return self._fallback_analysis(current_a, power_w, voltage_v)
    
    def _fallback_analysis(self, current_a: float, power_w: float, voltage_v: float = 5.0) -> Dict[str, Any]:
        """Fallback rule-based analysis when API fails"""
        
        if current_a > 1.5:
            return {
                "status": "warning",
                "analysis": f"High power draw: {current_a}A ({power_w}W)",
                "recommendation": "Monitor device temperature and power supply",
                "is_abnormal": False,
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        elif current_a > 0.1:
            return {
                "status": "normal",
                "analysis": f"Normal operation at {current_a}A ({power_w}W)",
                "recommendation": "System operating normally",
                "is_abnormal": False,
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "normal",
                "analysis": "Device in standby or disconnected",
                "recommendation": "No action needed",
                "is_abnormal": False,
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat()
            }
    
    def format_analysis_output(self, analysis: Dict[str, Any]) -> str:
        """
        Format analysis output for display
        
        Args:
            analysis: Analysis dict from analyze_power_data()
        
        Returns:
            Formatted string for console output
        """
        if not analysis:
            return "[ERROR] Analysis failed"
        
        status_icons = {
            "normal": "✅",
            "warning": "⚠️",
            "alert": "🚨",
            "error": "❌"
        }
        
        icon = status_icons.get(analysis.get("status", "normal"), "📊")
        abnormal_marker = " [ANOMALY DETECTED]" if analysis.get("is_abnormal") else ""
        
        confidence = analysis.get("confidence", 0)
        confidence_bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))
        
        return f"""
┌─────────────────────────────────────────────────┐
│ {icon} Power Analysis {abnormal_marker}                         │
├─────────────────────────────────────────────────┤
│ Status: {analysis.get('status', 'N/A').upper():<10} Confidence: [{confidence_bar}] {int(confidence*100)}% │
├─────────────────────────────────────────────────┤
│ Analysis:                                        │
│   {analysis.get('analysis', 'N/A')}             │
├─────────────────────────────────────────────────┤
│ Recommendation:                                  │
│   → {analysis.get('recommendation', 'N/A')}     │
└─────────────────────────────────────────────────┘"""


# For backward compatibility with existing code
class PowerAnalyzer(LLMClient):
    """Wrapper class for backward compatibility"""
    pass

# Make PowerAnalyzer available for import
__all__ = ['PowerAnalyzer', 'LLMClient']