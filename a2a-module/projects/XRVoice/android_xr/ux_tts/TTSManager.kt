package com.xrvoice.android_xr.ux_tts

import android.content.Context
import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import android.util.Log
import java.util.*
import java.util.concurrent.ConcurrentLinkedQueue
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Manages Android Text-to-Speech engine for XR voice feedback
 * Provides low-latency speech synthesis with queue management
 */
class TTSManager(private val context: Context) : TextToSpeech.OnInitListener {
    
    companion object {
        private const val TAG = "TTSManager"
        private const val DEFAULT_SPEECH_RATE = 1.0f
        private const val DEFAULT_PITCH = 1.0f
        private const val XR_SPEECH_RATE = 1.1f // Slightly faster for XR context
        private const val QUEUE_FLUSH = TextToSpeech.QUEUE_FLUSH
        private const val QUEUE_ADD = TextToSpeech.QUEUE_ADD
    }
    
    private var tts: TextToSpeech? = null
    private val speechQueue = ConcurrentLinkedQueue<SpeechRequest>()
    private val coroutineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    // State management
    private val _isInitialized = MutableStateFlow(false)
    val isInitialized: StateFlow<Boolean> = _isInitialized
    
    private val _isSpeaking = MutableStateFlow(false)
    val isSpeaking: StateFlow<Boolean> = _isSpeaking
    
    private val _currentVoice = MutableStateFlow<Voice?>(null)
    val currentVoice: StateFlow<Voice?> = _currentVoice
    
    // Voice configuration
    private var speechRate = XR_SPEECH_RATE
    private var pitch = DEFAULT_PITCH
    private var selectedLanguage = Locale.US
    
    // Callbacks
    private var onSpeechStarted: ((String) -> Unit)? = null
    private var onSpeechCompleted: ((String) -> Unit)? = null
    private var onSpeechError: ((String, String) -> Unit)? = null
    
    init {
        initializeTTS()
    }
    
    private fun initializeTTS() {
        Log.d(TAG, "Initializing TTS engine")
        tts = TextToSpeech(context, this)
    }
    
    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            Log.d(TAG, "TTS initialization successful")
            configureTTS()
            _isInitialized.value = true
            processQueue()
        } else {
            Log.e(TAG, "TTS initialization failed with status: $status")
            _isInitialized.value = false
        }
    }
    
    private fun configureTTS() {
        tts?.apply {
            // Set language
            val result = setLanguage(selectedLanguage)
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Log.w(TAG, "Language not fully supported: $selectedLanguage")
            }
            
            // Configure speech parameters
            setSpeechRate(speechRate)
            setPitch(pitch)
            
            // Select optimal voice for XR
            selectOptimalVoice()
            
            // Set up utterance listener
            setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String) {
                    Log.d(TAG, "Speech started: $utteranceId")
                    _isSpeaking.value = true
                    onSpeechStarted?.invoke(utteranceId)
                }
                
                override fun onDone(utteranceId: String) {
                    Log.d(TAG, "Speech completed: $utteranceId")
                    _isSpeaking.value = false
                    onSpeechCompleted?.invoke(utteranceId)
                    processQueue()
                }
                
                override fun onError(utteranceId: String) {
                    Log.e(TAG, "Speech error: $utteranceId")
                    _isSpeaking.value = false
                    onSpeechError?.invoke(utteranceId, "TTS error occurred")
                    processQueue()
                }
                
                @Deprecated("Deprecated in API 21")
                override fun onError(utteranceId: String?, errorCode: Int) {
                    onError(utteranceId ?: "unknown")
                }
            })
        }
    }
    
    private fun selectOptimalVoice() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            tts?.let { engine ->
                val voices = engine.voices
                
                // Filter for desired characteristics
                val optimalVoice = voices?.firstOrNull { voice ->
                    !voice.isNetworkConnectionRequired &&
                    voice.locale == selectedLanguage &&
                    voice.quality >= Voice.QUALITY_HIGH &&
                    !voice.features.contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED)
                }
                
                optimalVoice?.let {
                    engine.voice = it
                    _currentVoice.value = it
                    Log.d(TAG, "Selected voice: ${it.name}")
                }
            }
        }
    }
    
    /**
     * Speak text immediately with XR-optimized settings
     */
    fun speak(text: String, queueMode: Int = QUEUE_FLUSH): String {
        val utteranceId = "xr_${System.currentTimeMillis()}"
        
        if (!_isInitialized.value) {
            Log.w(TAG, "TTS not initialized, queueing speech")
            speechQueue.offer(SpeechRequest(text, utteranceId, queueMode))
            return utteranceId
        }
        
        if (queueMode == QUEUE_FLUSH) {
            speechQueue.clear()
        }
        
        val params = Bundle().apply {
            putString(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, utteranceId)
            putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, 1.0f)
            putInt(TextToSpeech.Engine.KEY_PARAM_STREAM, android.media.AudioManager.STREAM_MUSIC)
        }
        
        tts?.speak(text, queueMode, params, utteranceId)
        Log.d(TAG, "Speaking: $text with ID: $utteranceId")
        
        return utteranceId
    }
    
    /**
     * Speak with priority for critical XR feedback
     */
    fun speakPriority(text: String): String {
        stop() // Clear current speech
        return speak(text, QUEUE_FLUSH)
    }
    
    /**
     * Queue multiple utterances for sequential playback
     */
    fun queueSpeak(texts: List<String>) {
        texts.forEachIndexed { index, text ->
            val queueMode = if (index == 0) QUEUE_FLUSH else QUEUE_ADD
            speak(text, queueMode)
        }
    }
    
    /**
     * Process queued speech requests
     */
    private fun processQueue() {
        if (speechQueue.isNotEmpty() && !_isSpeaking.value) {
            speechQueue.poll()?.let { request ->
                speak(request.text, request.queueMode)
            }
        }
    }
    
    /**
     * Adjust speech rate for XR context
     */
    fun setSpeechRate(rate: Float) {
        speechRate = rate.coerceIn(0.5f, 2.0f)
        tts?.setSpeechRate(speechRate)
        Log.d(TAG, "Speech rate set to: $speechRate")
    }
    
    /**
     * Adjust pitch for voice character
     */
    fun setPitch(pitchValue: Float) {
        pitch = pitchValue.coerceIn(0.5f, 2.0f)
        tts?.setPitch(pitch)
        Log.d(TAG, "Pitch set to: $pitch")
    }
    
    /**
     * Change TTS language
     */
    fun setLanguage(locale: Locale): Boolean {
        selectedLanguage = locale
        val result = tts?.setLanguage(locale) ?: TextToSpeech.LANG_NOT_SUPPORTED
        return result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED
    }
    
    /**
     * Get available voices for current language
     */
    fun getAvailableVoices(): Set<Voice> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            tts?.voices?.filter { it.locale == selectedLanguage }?.toSet() ?: emptySet()
        } else {
            emptySet()
        }
    }
    
    /**
     * Set specific voice
     */
    fun setVoice(voice: Voice): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            tts?.voice = voice
            _currentVoice.value = voice
            true
        } else {
            false
        }
    }
    
    /**
     * Stop current speech
     */
    fun stop() {
        tts?.stop()
        _isSpeaking.value = false
        Log.d(TAG, "Speech stopped")
    }
    
    /**
     * Pause speech (if supported)
     */
    fun pause() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            // Note: Direct pause not available, using stop
            stop()
        }
    }
    
    /**
     * Set speech callbacks
     */
    fun setSpeechCallbacks(
        onStarted: ((String) -> Unit)? = null,
        onCompleted: ((String) -> Unit)? = null,
        onError: ((String, String) -> Unit)? = null
    ) {
        onSpeechStarted = onStarted
        onSpeechCompleted = onCompleted
        onSpeechError = onError
    }
    
    /**
     * Check if TTS is available
     */
    fun isAvailable(): Boolean = _isInitialized.value && tts != null
    
    /**
     * Get supported languages
     */
    fun getSupportedLanguages(): Set<Locale> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            tts?.availableLanguages ?: emptySet()
        } else {
            // Fallback for older versions
            setOf(Locale.US, Locale.UK, Locale.CANADA, Locale.FRENCH, Locale.GERMAN)
        }
    }
    
    /**
     * Clean up resources
     */
    fun shutdown() {
        Log.d(TAG, "Shutting down TTS")
        stop()
        speechQueue.clear()
        coroutineScope.cancel()
        tts?.shutdown()
        tts = null
        _isInitialized.value = false
    }
    
    /**
     * Data class for speech requests
     */
    private data class SpeechRequest(
        val text: String,
        val utteranceId: String,
        val queueMode: Int
    )
}