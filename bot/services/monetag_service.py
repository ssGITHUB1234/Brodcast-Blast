"""Monetag ads integration service"""
from config.settings import MONETAG_SDK_KEY, MONETAG_ZONE, MONETAG_SDK_FUNC

class MonetgService:
    """Service for Monetag ads management"""
    
    def __init__(self):
        self.zone_id = MONETAG_ZONE
        self.sdk_func = MONETAG_SDK_FUNC
        self.is_enabled = bool(MONETAG_SDK_KEY)
    
    def get_sdk_script(self):
        """Get Monetag SDK script tag for HTML"""
        if not self.is_enabled:
            return ""
        return f"<script src='//libtl.com/sdk.js' data-zone='{self.zone_id}' data-sdk='{self.sdk_func}'></script>"
    
    def get_ad_config(self):
        """Get ad configuration for client"""
        return {
            'enabled': self.is_enabled,
            'zone_id': self.zone_id,
            'sdk_func': self.sdk_func
        }
    
    def get_rewarded_ad_function(self):
        """Get rewarded ad function call"""
        return f"{self.sdk_func}().then(() => {{ /* user reward function */ }})"
    
    def get_rewarded_popup_function(self):
        """Get rewarded popup ad function call"""
        return f"{self.sdk_func}('pop').then(() => {{ /* reward on completion */ }}).catch(e => {{ /* handle error */ }})"
    
    def get_inapp_interstitial_function(self):
        """Get in-app interstitial ad function call"""
        return f"""{self.sdk_func}({{
            type: 'inApp',
            inAppSettings: {{
                frequency: 2,
                capping: 0.1,
                interval: 30,
                timeout: 5,
                everyPage: false
            }}
        }})"""
