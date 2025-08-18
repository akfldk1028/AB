package com.xrvoice.android_xr.ux_tts

import android.content.Context
import android.media.AudioManager
import android.os.VibrationEffect
import android.os.Vibrator
import android.util.Log
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.util.concurrent.ConcurrentHashMap

/**
 * Coordinates TTS output with HUD visual feedback for immersive XR experience
 * Manages synchronized audio-visual responses to user interactions
 */
class VoiceFeedbackController(private val context: Context) {
    
    companion object {
        private const val TAG = "VoiceFeedbackController"
        private const val HAPTIC_DURATION = 50L
        private const val VOICE_QUEUE_LIMIT = 10
        private const val FEEDBACK_DELAY_MS = 100L
    }
    
    // Core components
    private val ttsManager = TTSManager(context)
    private var hudOverlayView: HUDOverlayView? = null
    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    
    // Coroutine scope for async operations
    private val controllerScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    // State management
    private val _isActive = MutableStateFlow(false)
    val isActive: StateFlow<Boolean> = _isActive
    
    private val _currentMode = MutableStateFlow(FeedbackMode.NORMAL)
    val currentMode: StateFlow<FeedbackMode> = _currentMode
    
    private val _voiceQueueSize = MutableStateFlow(0)
    val voiceQueueSize: StateFlow<Int> = _voiceQueueSize
    
    // Response templates
    private val responseTemplates = ConcurrentHashMap<ResponseType, ResponseTemplate>()
    
    // Feedback profiles
    private val feedbackProfiles = mapOf(
        FeedbackMode.NORMAL to FeedbackProfile(
            ttsRate = 1.0f,
            ttsPitch = 1.0f,
            crosshairStyle = CrosshairRenderer.CrosshairStyle.DYNAMIC_CROSS,
            hapticEnabled = true,
            visualFeedbackEnabled = true
        ),
        FeedbackMode.FAST to FeedbackProfile(
            ttsRate = 1.3f,
            ttsPitch = 1.1f,
            crosshairStyle = CrosshairRenderer.CrosshairStyle.SIMPLE_CROSS,
            hapticEnabled = false,
            visualFeedbackEnabled = true
        ),
        FeedbackMode.QUIET to FeedbackProfile(
            ttsRate = 0.9f,
            ttsPitch = 0.9f,
            crosshairStyle = CrosshairRenderer.CrosshairStyle.DOT,
            hapticEnabled = false,
            visualFeedbackEnabled = false
        ),
        FeedbackMode.EMERGENCY to FeedbackProfile(
            ttsRate = 1.2f,
            ttsPitch = 1.2f,
            crosshairStyle = CrosshairRenderer.CrosshairStyle.TRIANGULAR,
            hapticEnabled = true,
            visualFeedbackEnabled = true
        )
    )
    
    enum class FeedbackMode {
        NORMAL, FAST, QUIET, EMERGENCY
    }
    
    enum class ResponseType {
        DETECTION, CONFIRMATION, ERROR, WARNING, INFO, SUCCESS, NAVIGATION, INTERACTION
    }
    
    init {
        initializeTemplates()
        setupTTSCallbacks()
        
        // Monitor TTS initialization
        controllerScope.launch {
            ttsManager.isInitialized.collect { initialized ->
                if (initialized) {
                    Log.d(TAG, "TTS initialized successfully")
                    applyFeedbackProfile(feedbackProfiles[_currentMode.value]!!)
                }
            }
        }
    }
    
    private fun initializeTemplates() {
        responseTemplates[ResponseType.DETECTION] = ResponseTemplate(
            phrases = listOf("Object detected", "Target acquired", "Item found"),
            hudNotificationType = HUDOverlayView.NotificationType.INFO,
            crosshairFeedback = CrosshairRenderer.FeedbackType.PULSE
        )
        
        responseTemplates[ResponseType.CONFIRMATION] = ResponseTemplate(
            phrases = listOf("Confirmed", "Acknowledged", "Understood"),
            hudNotificationType = HUDOverlayView.NotificationType.SUCCESS,
            crosshairFeedback = CrosshairRenderer.FeedbackType.SCALE
        )
        
        responseTemplates[ResponseType.ERROR] = ResponseTemplate(
            phrases = listOf("Error occurred", "Operation failed", "Unable to process"),
            hudNotificationType = HUDOverlayView.NotificationType.ERROR,
            crosshairFeedback = CrosshairRenderer.FeedbackType.COLOR_CHANGE
        )
        
        responseTemplates[ResponseType.WARNING] = ResponseTemplate(
            phrases = listOf("Warning", "Caution advised", "Attention required"),
            hudNotificationType = HUDOverlayView.NotificationType.WARNING,
            crosshairFeedback = CrosshairRenderer.FeedbackType.PULSE
        )
        
        responseTemplates[ResponseType.INFO] = ResponseTemplate(
            phrases = listOf("Information available", "Data received", "Update ready"),
            hudNotificationType = HUDOverlayView.NotificationType.INFO,
            crosshairFeedback = CrosshairRenderer.FeedbackType.NONE
        )
        
        responseTemplates[ResponseType.SUCCESS] = ResponseTemplate(
            phrases = listOf("Success", "Operation complete", "Task finished"),
            hudNotificationType = HUDOverlayView.NotificationType.SUCCESS,
            crosshairFeedback = CrosshairRenderer.FeedbackType.HIT_MARKER
        )
        
        responseTemplates[ResponseType.NAVIGATION] = ResponseTemplate(
            phrases = listOf("Navigate to", "Direction updated", "Path calculated"),
            hudNotificationType = HUDOverlayView.NotificationType.INFO,
            crosshairFeedback = CrosshairRenderer.FeedbackType.ROTATION
        )
        
        responseTemplates[ResponseType.INTERACTION] = ResponseTemplate(
            phrases = listOf("Interaction available", "Gesture recognized", "Input received"),
            hudNotificationType = HUDOverlayView.NotificationType.INFO,
            crosshairFeedback = CrosshairRenderer.FeedbackType.SCALE
        )
    }
    
    private fun setupTTSCallbacks() {
        ttsManager.setSpeechCallbacks(
            onStarted = { utteranceId ->
                Log.d(TAG, "Speech started: $utteranceId")
                hudOverlayView?.setCrosshairActive(true)
                updateVoiceQueueSize(-1)
            },
            onCompleted = { utteranceId ->
                Log.d(TAG, "Speech completed: $utteranceId")
                hudOverlayView?.setCrosshairActive(false)
            },
            onError = { utteranceId, error ->
                Log.e(TAG, "Speech error for $utteranceId: $error")
                hudOverlayView?.showNotification(
                    "Voice output error",
                    HUDOverlayView.NotificationType.ERROR
                )
            }
        )
    }
    
    /**
     * Attach HUD overlay view
     */
    fun attachHUDOverlay(overlay: HUDOverlayView) {
        hudOverlayView = overlay
        applyFeedbackProfile(feedbackProfiles[_currentMode.value]!!)
        Log.d(TAG, "HUD overlay attached")
    }
    
    /**
     * Provide voice feedback with synchronized HUD response
     */
    fun provideFeedback(
        text: String,
        responseType: ResponseType = ResponseType.INFO,
        priority: Boolean = false
    ) {
        if (!_isActive.value) {
            Log.w(TAG, "Controller not active, feedback ignored")
            return
        }
        
        controllerScope.launch {
            // Check queue limit
            if (_voiceQueueSize.value >= VOICE_QUEUE_LIMIT && !priority) {
                Log.w(TAG, "Voice queue full, dropping feedback")
                return@launch
            }
            
            updateVoiceQueueSize(1)
            
            // Get response template
            val template = responseTemplates[responseType] ?: responseTemplates[ResponseType.INFO]!!
            
            // Trigger haptic feedback
            if (feedbackProfiles[_currentMode.value]?.hapticEnabled == true) {
                provideHapticFeedback(responseType)
            }
            
            // Show HUD notification
            if (feedbackProfiles[_currentMode.value]?.visualFeedbackEnabled == true) {
                hudOverlayView?.showNotification(text, template.hudNotificationType)
                hudOverlayView?.triggerCrosshairFeedback(template.crosshairFeedback)
            }
            
            // Speak text
            delay(FEEDBACK_DELAY_MS)
            if (priority) {
                ttsManager.speakPriority(text)
            } else {
                ttsManager.speak(text)
            }
        }
    }
    
    /**
     * Provide templated feedback
     */
    fun provideTemplatedFeedback(
        responseType: ResponseType,
        customText: String? = null,
        priority: Boolean = false
    ) {
        val template = responseTemplates[responseType] ?: return
        val text = customText ?: template.phrases.random()
        provideFeedback(text, responseType, priority)
    }
    
    /**
     * Provide navigation feedback
     */
    fun provideNavigationFeedback(direction: String, distance: Float? = null) {
        val text = buildString {
            append(direction)
            distance?.let {
                append(", ${it.toInt()} meters")
            }
        }
        provideFeedback(text, ResponseType.NAVIGATION)
    }
    
    /**
     * Provide object detection feedback
     */
    fun provideDetectionFeedback(objectName: String, confidence: Float? = null) {
        val text = buildString {
            append("$objectName detected")
            confidence?.let {
                if (it < 0.7f) append(", low confidence")
            }
        }
        provideFeedback(text, ResponseType.DETECTION)
    }
    
    /**
     * Set feedback mode
     */
    fun setFeedbackMode(mode: FeedbackMode) {
        _currentMode.value = mode
        feedbackProfiles[mode]?.let { profile ->
            applyFeedbackProfile(profile)
        }
        Log.d(TAG, "Feedback mode changed to: $mode")
    }
    
    private fun applyFeedbackProfile(profile: FeedbackProfile) {
        // Configure TTS
        ttsManager.setSpeechRate(profile.ttsRate)
        ttsManager.setPitch(profile.ttsPitch)
        
        // Configure HUD
        hudOverlayView?.configureCrosshair(profile.crosshairStyle)
        
        Log.d(TAG, "Applied feedback profile: $profile")
    }
    
    private fun provideHapticFeedback(responseType: ResponseType) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            val effect = when (responseType) {
                ResponseType.ERROR, ResponseType.WARNING -> {
                    VibrationEffect.createOneShot(HAPTIC_DURATION * 2, VibrationEffect.DEFAULT_AMPLITUDE)
                }
                ResponseType.SUCCESS, ResponseType.CONFIRMATION -> {
                    VibrationEffect.createOneShot(HAPTIC_DURATION, VibrationEffect.DEFAULT_AMPLITUDE)
                }
                else -> {
                    VibrationEffect.createOneShot(HAPTIC_DURATION / 2, VibrationEffect.DEFAULT_AMPLITUDE / 2)
                }
            }
            vibrator?.vibrate(effect)
        } else {
            @Suppress("DEPRECATION")
            vibrator?.vibrate(HAPTIC_DURATION)
        }
    }
    
    private fun updateVoiceQueueSize(delta: Int) {
        _voiceQueueSize.update { current ->
            (current + delta).coerceAtLeast(0)
        }
    }
    
    /**
     * Start controller
     */
    fun start() {
        _isActive.value = true
        hudOverlayView?.setOverlayActive(true)
        
        // Add status indicators
        hudOverlayView?.addStatusIndicator(
            "tts_status",
            "TTS",
            if (ttsManager.isAvailable()) android.graphics.Color.GREEN else android.graphics.Color.RED,
            HUDOverlayView.IndicatorShape.CIRCLE
        )
        
        Log.d(TAG, "Voice feedback controller started")
    }
    
    /**
     * Stop controller
     */
    fun stop() {
        _isActive.value = false
        ttsManager.stop()
        hudOverlayView?.setOverlayActive(false)
        Log.d(TAG, "Voice feedback controller stopped")
    }
    
    /**
     * Pause voice output
     */
    fun pauseVoice() {
        ttsManager.pause()
    }
    
    /**
     * Resume voice output
     */
    fun resumeVoice() {
        if (_isActive.value) {
            // Resume by processing any queued items
            Log.d(TAG, "Voice output resumed")
        }
    }
    
    /**
     * Clear voice queue
     */
    fun clearVoiceQueue() {
        ttsManager.stop()
        _voiceQueueSize.value = 0
        Log.d(TAG, "Voice queue cleared")
    }
    
    /**
     * Check audio focus
     */
    fun requestAudioFocus(): Boolean {
        val result = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            val focusRequest = android.media.AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
                .setAudioAttributes(
                    android.media.AudioAttributes.Builder()
                        .setUsage(android.media.AudioAttributes.USAGE_ASSISTANT)
                        .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
                .setAcceptsDelayedFocusGain(true)
                .build()
            
            audioManager.requestAudioFocus(focusRequest)
        } else {
            @Suppress("DEPRECATION")
            audioManager.requestAudioFocus(
                null,
                AudioManager.STREAM_MUSIC,
                AudioManager.AUDIOFOCUS_GAIN_TRANSIENT
            )
        }
        
        return result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED
    }
    
    /**
     * Release audio focus
     */
    fun releaseAudioFocus() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            // Would need to store focusRequest to abandon it
        } else {
            @Suppress("DEPRECATION")
            audioManager.abandonAudioFocus(null)
        }
    }
    
    /**
     * Clean up resources
     */
    fun cleanup() {
        stop()
        controllerScope.cancel()
        ttsManager.shutdown()
        hudOverlayView?.cleanup()
        hudOverlayView = null
        responseTemplates.clear()
        Log.d(TAG, "Controller cleaned up")
    }
    
    // Data classes
    private data class ResponseTemplate(
        val phrases: List<String>,
        val hudNotificationType: HUDOverlayView.NotificationType,
        val crosshairFeedback: CrosshairRenderer.FeedbackType
    )
    
    private data class FeedbackProfile(
        val ttsRate: Float,
        val ttsPitch: Float,
        val crosshairStyle: CrosshairRenderer.CrosshairStyle,
        val hapticEnabled: Boolean,
        val visualFeedbackEnabled: Boolean
    )
}