package com.xrvoice.android_xr.ux_tts

import android.content.Context
import android.content.SharedPreferences
import android.graphics.Color
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.Locale

/**
 * Configuration manager for XR display and TTS settings
 * Handles persistent storage and runtime configuration updates
 */
class XRDisplayConfig(context: Context) {
    
    companion object {
        private const val PREFS_NAME = "xr_display_config"
        private const val KEY_CROSSHAIR_STYLE = "crosshair_style"
        private const val KEY_CROSSHAIR_SIZE = "crosshair_size"
        private const val KEY_CROSSHAIR_COLOR = "crosshair_color"
        private const val KEY_CROSSHAIR_ACTIVE_COLOR = "crosshair_active_color"
        private const val KEY_TTS_ENABLED = "tts_enabled"
        private const val KEY_TTS_RATE = "tts_rate"
        private const val KEY_TTS_PITCH = "tts_pitch"
        private const val KEY_TTS_LANGUAGE = "tts_language"
        private const val KEY_HUD_ENABLED = "hud_enabled"
        private const val KEY_HUD_OPACITY = "hud_opacity"
        private const val KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
        private const val KEY_HAPTIC_ENABLED = "haptic_enabled"
        private const val KEY_FEEDBACK_MODE = "feedback_mode"
        private const val KEY_AUDIO_DUCKING = "audio_ducking"
        private const val KEY_ACCESSIBILITY_MODE = "accessibility_mode"
        
        // Default values
        private const val DEFAULT_CROSSHAIR_SIZE = 50f
        private const val DEFAULT_TTS_RATE = 1.0f
        private const val DEFAULT_TTS_PITCH = 1.0f
        private const val DEFAULT_HUD_OPACITY = 0.8f
    }
    
    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    
    // Observable configuration states
    private val _crosshairConfig = MutableStateFlow(loadCrosshairConfig())
    val crosshairConfig: StateFlow<CrosshairConfig> = _crosshairConfig
    
    private val _ttsConfig = MutableStateFlow(loadTTSConfig())
    val ttsConfig: StateFlow<TTSConfig> = _ttsConfig
    
    private val _hudConfig = MutableStateFlow(loadHUDConfig())
    val hudConfig: StateFlow<HUDConfig> = _hudConfig
    
    private val _feedbackConfig = MutableStateFlow(loadFeedbackConfig())
    val feedbackConfig: StateFlow<FeedbackConfig> = _feedbackConfig
    
    private val _accessibilityConfig = MutableStateFlow(loadAccessibilityConfig())
    val accessibilityConfig: StateFlow<AccessibilityConfig> = _accessibilityConfig
    
    // Configuration data classes
    data class CrosshairConfig(
        val style: CrosshairRenderer.CrosshairStyle,
        val size: Float,
        val thickness: Float,
        val gap: Float,
        val baseColor: Int,
        val activeColor: Int,
        val errorColor: Int,
        val animationEnabled: Boolean
    )
    
    data class TTSConfig(
        val enabled: Boolean,
        val rate: Float,
        val pitch: Float,
        val language: String,
        val voiceId: String?,
        val queueMode: Int,
        val audioDucking: Boolean
    )
    
    data class HUDConfig(
        val enabled: Boolean,
        val opacity: Float,
        val notificationsEnabled: Boolean,
        val notificationDuration: Long,
        val statusIndicatorsEnabled: Boolean,
        val compassEnabled: Boolean,
        val distanceIndicatorEnabled: Boolean
    )
    
    data class FeedbackConfig(
        val mode: VoiceFeedbackController.FeedbackMode,
        val hapticEnabled: Boolean,
        val hapticIntensity: Float,
        val visualFeedbackEnabled: Boolean,
        val audioFeedbackEnabled: Boolean,
        val adaptiveMode: Boolean
    )
    
    data class AccessibilityConfig(
        val enabled: Boolean,
        val highContrastMode: Boolean,
        val largeTextMode: Boolean,
        val colorBlindMode: ColorBlindMode,
        val reducedMotion: Boolean,
        val verboseMode: Boolean
    )
    
    enum class ColorBlindMode {
        NONE, PROTANOPIA, DEUTERANOPIA, TRITANOPIA
    }
    
    // Load configuration methods
    private fun loadCrosshairConfig(): CrosshairConfig {
        return CrosshairConfig(
            style = CrosshairRenderer.CrosshairStyle.valueOf(
                prefs.getString(KEY_CROSSHAIR_STYLE, CrosshairRenderer.CrosshairStyle.DYNAMIC_CROSS.name)!!
            ),
            size = prefs.getFloat(KEY_CROSSHAIR_SIZE, DEFAULT_CROSSHAIR_SIZE),
            thickness = prefs.getFloat("crosshair_thickness", 3f),
            gap = prefs.getFloat("crosshair_gap", 10f),
            baseColor = prefs.getInt(KEY_CROSSHAIR_COLOR, Color.WHITE),
            activeColor = prefs.getInt(KEY_CROSSHAIR_ACTIVE_COLOR, Color.GREEN),
            errorColor = prefs.getInt("crosshair_error_color", Color.RED),
            animationEnabled = prefs.getBoolean("crosshair_animation", true)
        )
    }
    
    private fun loadTTSConfig(): TTSConfig {
        return TTSConfig(
            enabled = prefs.getBoolean(KEY_TTS_ENABLED, true),
            rate = prefs.getFloat(KEY_TTS_RATE, DEFAULT_TTS_RATE),
            pitch = prefs.getFloat(KEY_TTS_PITCH, DEFAULT_TTS_PITCH),
            language = prefs.getString(KEY_TTS_LANGUAGE, Locale.US.toString())!!,
            voiceId = prefs.getString("tts_voice_id", null),
            queueMode = prefs.getInt("tts_queue_mode", 0),
            audioDucking = prefs.getBoolean(KEY_AUDIO_DUCKING, true)
        )
    }
    
    private fun loadHUDConfig(): HUDConfig {
        return HUDConfig(
            enabled = prefs.getBoolean(KEY_HUD_ENABLED, true),
            opacity = prefs.getFloat(KEY_HUD_OPACITY, DEFAULT_HUD_OPACITY),
            notificationsEnabled = prefs.getBoolean(KEY_NOTIFICATIONS_ENABLED, true),
            notificationDuration = prefs.getLong("notification_duration", 3000L),
            statusIndicatorsEnabled = prefs.getBoolean("status_indicators", true),
            compassEnabled = prefs.getBoolean("compass_enabled", false),
            distanceIndicatorEnabled = prefs.getBoolean("distance_indicator", false)
        )
    }
    
    private fun loadFeedbackConfig(): FeedbackConfig {
        return FeedbackConfig(
            mode = VoiceFeedbackController.FeedbackMode.valueOf(
                prefs.getString(KEY_FEEDBACK_MODE, VoiceFeedbackController.FeedbackMode.NORMAL.name)!!
            ),
            hapticEnabled = prefs.getBoolean(KEY_HAPTIC_ENABLED, true),
            hapticIntensity = prefs.getFloat("haptic_intensity", 1.0f),
            visualFeedbackEnabled = prefs.getBoolean("visual_feedback", true),
            audioFeedbackEnabled = prefs.getBoolean("audio_feedback", true),
            adaptiveMode = prefs.getBoolean("adaptive_mode", false)
        )
    }
    
    private fun loadAccessibilityConfig(): AccessibilityConfig {
        return AccessibilityConfig(
            enabled = prefs.getBoolean(KEY_ACCESSIBILITY_MODE, false),
            highContrastMode = prefs.getBoolean("high_contrast", false),
            largeTextMode = prefs.getBoolean("large_text", false),
            colorBlindMode = ColorBlindMode.valueOf(
                prefs.getString("color_blind_mode", ColorBlindMode.NONE.name)!!
            ),
            reducedMotion = prefs.getBoolean("reduced_motion", false),
            verboseMode = prefs.getBoolean("verbose_mode", false)
        )
    }
    
    // Update configuration methods
    fun updateCrosshairConfig(update: CrosshairConfig.() -> CrosshairConfig) {
        val newConfig = _crosshairConfig.value.update()
        _crosshairConfig.value = newConfig
        saveCrosshairConfig(newConfig)
    }
    
    fun updateTTSConfig(update: TTSConfig.() -> TTSConfig) {
        val newConfig = _ttsConfig.value.update()
        _ttsConfig.value = newConfig
        saveTTSConfig(newConfig)
    }
    
    fun updateHUDConfig(update: HUDConfig.() -> HUDConfig) {
        val newConfig = _hudConfig.value.update()
        _hudConfig.value = newConfig
        saveHUDConfig(newConfig)
    }
    
    fun updateFeedbackConfig(update: FeedbackConfig.() -> FeedbackConfig) {
        val newConfig = _feedbackConfig.value.update()
        _feedbackConfig.value = newConfig
        saveFeedbackConfig(newConfig)
    }
    
    fun updateAccessibilityConfig(update: AccessibilityConfig.() -> AccessibilityConfig) {
        val newConfig = _accessibilityConfig.value.update()
        _accessibilityConfig.value = newConfig
        saveAccessibilityConfig(newConfig)
    }
    
    // Save configuration methods
    private fun saveCrosshairConfig(config: CrosshairConfig) {
        prefs.edit().apply {
            putString(KEY_CROSSHAIR_STYLE, config.style.name)
            putFloat(KEY_CROSSHAIR_SIZE, config.size)
            putFloat("crosshair_thickness", config.thickness)
            putFloat("crosshair_gap", config.gap)
            putInt(KEY_CROSSHAIR_COLOR, config.baseColor)
            putInt(KEY_CROSSHAIR_ACTIVE_COLOR, config.activeColor)
            putInt("crosshair_error_color", config.errorColor)
            putBoolean("crosshair_animation", config.animationEnabled)
            apply()
        }
    }
    
    private fun saveTTSConfig(config: TTSConfig) {
        prefs.edit().apply {
            putBoolean(KEY_TTS_ENABLED, config.enabled)
            putFloat(KEY_TTS_RATE, config.rate)
            putFloat(KEY_TTS_PITCH, config.pitch)
            putString(KEY_TTS_LANGUAGE, config.language)
            putString("tts_voice_id", config.voiceId)
            putInt("tts_queue_mode", config.queueMode)
            putBoolean(KEY_AUDIO_DUCKING, config.audioDucking)
            apply()
        }
    }
    
    private fun saveHUDConfig(config: HUDConfig) {
        prefs.edit().apply {
            putBoolean(KEY_HUD_ENABLED, config.enabled)
            putFloat(KEY_HUD_OPACITY, config.opacity)
            putBoolean(KEY_NOTIFICATIONS_ENABLED, config.notificationsEnabled)
            putLong("notification_duration", config.notificationDuration)
            putBoolean("status_indicators", config.statusIndicatorsEnabled)
            putBoolean("compass_enabled", config.compassEnabled)
            putBoolean("distance_indicator", config.distanceIndicatorEnabled)
            apply()
        }
    }
    
    private fun saveFeedbackConfig(config: FeedbackConfig) {
        prefs.edit().apply {
            putString(KEY_FEEDBACK_MODE, config.mode.name)
            putBoolean(KEY_HAPTIC_ENABLED, config.hapticEnabled)
            putFloat("haptic_intensity", config.hapticIntensity)
            putBoolean("visual_feedback", config.visualFeedbackEnabled)
            putBoolean("audio_feedback", config.audioFeedbackEnabled)
            putBoolean("adaptive_mode", config.adaptiveMode)
            apply()
        }
    }
    
    private fun saveAccessibilityConfig(config: AccessibilityConfig) {
        prefs.edit().apply {
            putBoolean(KEY_ACCESSIBILITY_MODE, config.enabled)
            putBoolean("high_contrast", config.highContrastMode)
            putBoolean("large_text", config.largeTextMode)
            putString("color_blind_mode", config.colorBlindMode.name)
            putBoolean("reduced_motion", config.reducedMotion)
            putBoolean("verbose_mode", config.verboseMode)
            apply()
        }
    }
    
    // Preset configurations
    fun applyPreset(preset: ConfigPreset) {
        when (preset) {
            ConfigPreset.DEFAULT -> resetToDefaults()
            ConfigPreset.GAMING -> applyGamingPreset()
            ConfigPreset.PRODUCTIVITY -> applyProductivityPreset()
            ConfigPreset.ACCESSIBILITY -> applyAccessibilityPreset()
            ConfigPreset.MINIMAL -> applyMinimalPreset()
        }
    }
    
    private fun resetToDefaults() {
        prefs.edit().clear().apply()
        _crosshairConfig.value = loadCrosshairConfig()
        _ttsConfig.value = loadTTSConfig()
        _hudConfig.value = loadHUDConfig()
        _feedbackConfig.value = loadFeedbackConfig()
        _accessibilityConfig.value = loadAccessibilityConfig()
    }
    
    private fun applyGamingPreset() {
        updateCrosshairConfig {
            copy(
                style = CrosshairRenderer.CrosshairStyle.SIMPLE_CROSS,
                size = 40f,
                animationEnabled = true
            )
        }
        updateFeedbackConfig {
            copy(
                mode = VoiceFeedbackController.FeedbackMode.FAST,
                hapticEnabled = true,
                visualFeedbackEnabled = true
            )
        }
    }
    
    private fun applyProductivityPreset() {
        updateCrosshairConfig {
            copy(
                style = CrosshairRenderer.CrosshairStyle.DOT,
                size = 30f,
                animationEnabled = false
            )
        }
        updateFeedbackConfig {
            copy(
                mode = VoiceFeedbackController.FeedbackMode.NORMAL,
                hapticEnabled = false
            )
        }
    }
    
    private fun applyAccessibilityPreset() {
        updateAccessibilityConfig {
            copy(
                enabled = true,
                highContrastMode = true,
                largeTextMode = true,
                verboseMode = true
            )
        }
        updateTTSConfig {
            copy(
                rate = 0.9f,
                pitch = 1.0f
            )
        }
    }
    
    private fun applyMinimalPreset() {
        updateHUDConfig {
            copy(
                enabled = true,
                opacity = 0.5f,
                notificationsEnabled = false,
                statusIndicatorsEnabled = false,
                compassEnabled = false,
                distanceIndicatorEnabled = false
            )
        }
        updateCrosshairConfig {
            copy(
                style = CrosshairRenderer.CrosshairStyle.DOT,
                size = 20f
            )
        }
    }
    
    enum class ConfigPreset {
        DEFAULT, GAMING, PRODUCTIVITY, ACCESSIBILITY, MINIMAL
    }
    
    /**
     * Export configuration as JSON
     */
    fun exportConfiguration(): String {
        return buildString {
            append("{")
            append("\"crosshair\":${configToJson(_crosshairConfig.value)},")
            append("\"tts\":${configToJson(_ttsConfig.value)},")
            append("\"hud\":${configToJson(_hudConfig.value)},")
            append("\"feedback\":${configToJson(_feedbackConfig.value)},")
            append("\"accessibility\":${configToJson(_accessibilityConfig.value)}")
            append("}")
        }
    }
    
    private fun configToJson(config: Any): String {
        // Simple JSON serialization (in production, use a proper JSON library)
        return when (config) {
            is CrosshairConfig -> {
                "{\"style\":\"${config.style}\",\"size\":${config.size}," +
                "\"thickness\":${config.thickness},\"gap\":${config.gap}," +
                "\"baseColor\":${config.baseColor},\"activeColor\":${config.activeColor}," +
                "\"errorColor\":${config.errorColor},\"animationEnabled\":${config.animationEnabled}}"
            }
            is TTSConfig -> {
                "{\"enabled\":${config.enabled},\"rate\":${config.rate}," +
                "\"pitch\":${config.pitch},\"language\":\"${config.language}\"," +
                "\"voiceId\":${config.voiceId?.let { "\"$it\"" } ?: "null"}," +
                "\"queueMode\":${config.queueMode},\"audioDucking\":${config.audioDucking}}"
            }
            is HUDConfig -> {
                "{\"enabled\":${config.enabled},\"opacity\":${config.opacity}," +
                "\"notificationsEnabled\":${config.notificationsEnabled}," +
                "\"notificationDuration\":${config.notificationDuration}," +
                "\"statusIndicatorsEnabled\":${config.statusIndicatorsEnabled}," +
                "\"compassEnabled\":${config.compassEnabled}," +
                "\"distanceIndicatorEnabled\":${config.distanceIndicatorEnabled}}"
            }
            is FeedbackConfig -> {
                "{\"mode\":\"${config.mode}\",\"hapticEnabled\":${config.hapticEnabled}," +
                "\"hapticIntensity\":${config.hapticIntensity}," +
                "\"visualFeedbackEnabled\":${config.visualFeedbackEnabled}," +
                "\"audioFeedbackEnabled\":${config.audioFeedbackEnabled}," +
                "\"adaptiveMode\":${config.adaptiveMode}}"
            }
            is AccessibilityConfig -> {
                "{\"enabled\":${config.enabled},\"highContrastMode\":${config.highContrastMode}," +
                "\"largeTextMode\":${config.largeTextMode}," +
                "\"colorBlindMode\":\"${config.colorBlindMode}\"," +
                "\"reducedMotion\":${config.reducedMotion},\"verboseMode\":${config.verboseMode}}"
            }
            else -> "{}"
        }
    }
}