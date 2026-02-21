##############################################################################
#
# PySwitch Configuration
# MIDI Captain Mini 6 - Multi-Device Controller
#
##############################################################################

Config = {
    
    # ==========================================================================
    # CORE SETTINGS
    # ==========================================================================
    
    # Max. number of MIDI messages being parsed before the next switch state 
    # evaluation. Default is 10.
    "maxConsecutiveMidiMessages": 10,

    # Clear MIDI buffer before starting processing. Default is True.
    "clearBuffers": True,                 

    # Update interval in milliseconds. Default is 200.
    "updateInterval": 200,

    # ==========================================================================
    # MEMORY AND PERFORMANCE
    # ==========================================================================
    
    # Amount of bytes that must be free when processing starts. 
    # Default threshold is 15kB.
    "memoryWarnLimitBytes": 1024 * 15,

    # ==========================================================================
    # WEB INTERFACE SUPPORT
    # ==========================================================================
    
    # Enables file transfer via MIDI from the PySwitch web interface
    # (https://pyswitch.tunetown.de/). Uses about 11kB of RAM.
    # Set to False if you run into memory issues.
    "enableMidiBridge": True,

    # ==========================================================================
    # LED BRIGHTNESS
    # ==========================================================================
    
    # Global brightness values for LEDs (0.0 to 1.0)
    "ledBrightnessOn": 0.3,
    "ledBrightnessOff": 0.02,

    # ==========================================================================
    # DISPLAY SETTINGS
    # ==========================================================================
    
    # Dim factors for display labels
    "displayDimFactorOn": 1,
    "displayDimFactorOff": 0.2,

    # ==========================================================================
    # COMBO DETECTION (used by MultiPageController)
    # ==========================================================================
    
    "comboDetection": {
        "enabled": True,
        "combo_switches": ['A', 'B', 'C'],
        "combo_window_ms": 50,
    },

    # ==========================================================================
    # DEBUG OPTIONS (uncomment to enable)
    # ==========================================================================
    
    # Show runtime and memory usage info
    #"debugStats": True,
    #"debugStatsInterval": 2000,
    
    # Debug bidirectional protocol
    #"debugBidirectionalProtocol": True,
    
    # Show unparsed incoming MIDI messages
    #"debugUnparsedMessages": True,
    
    # Show sent MIDI messages
    #"debugSentMessages": True,
    
    # Exclude specific message types from debug output
    #"excludeMessageTypes": ["SystemExclusive"],
    
    # ==========================================================================
    # EXPLORE MODE (for hardware debugging)
    # ==========================================================================
    
    # Set to True to boot into explore mode (shows GPIO pins and cycles LEDs)
    #"exploreMode": True
}
