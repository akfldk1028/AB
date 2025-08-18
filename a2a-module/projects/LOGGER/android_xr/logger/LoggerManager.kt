package com.xr.logger

import android.content.Context
import timber.log.Timber
import java.util.concurrent.ConcurrentHashMap

/**
 * Centralized logging manager for Android XR applications
 * Provides unified interface for all logging operations
 */
object LoggerManager {
    
    private var isInitialized = false
    private var fileLoggingTree: FileLoggingTree? = null
    private var performanceTree: PerformanceLoggingTree? = null
    private val logTags = ConcurrentHashMap<String, Boolean>()
    private var globalLogLevel = LogLevel.DEBUG
    
    enum class LogLevel(val priority: Int) {
        VERBOSE(2),
        DEBUG(3),
        INFO(4),
        WARN(5),
        ERROR(6),
        NONE(7)
    }
    
    /**
     * Initialize the logging system
     */
    fun initialize(context: Context, config: LogConfig = LogConfig()) {
        if (isInitialized) {
            Timber.w("LoggerManager already initialized")
            return
        }
        
        // Initialize Timber with configuration
        TimberConfiguration.initialize(context, config.isDebug)
        
        // Store references to special trees
        if (config.enableFileLogging) {
            val logDir = java.io.File(context.filesDir, "logs")
            fileLoggingTree = FileLoggingTree(
                logDirectory = logDir,
                maxFileSize = config.maxFileSize,
                maxFileCount = config.maxFileCount
            )
        }
        
        if (config.enablePerformanceLogging) {
            performanceTree = PerformanceLoggingTree()
        }
        
        globalLogLevel = config.minLogLevel
        isInitialized = true
        
        Timber.i("LoggerManager initialized with config: $config")
    }
    
    /**
     * Log verbose message
     */
    fun v(tag: String, message: String, vararg args: Any) {
        if (shouldLog(tag, LogLevel.VERBOSE)) {
            Timber.tag(tag).v(message, *args)
        }
    }
    
    /**
     * Log debug message
     */
    fun d(tag: String, message: String, vararg args: Any) {
        if (shouldLog(tag, LogLevel.DEBUG)) {
            Timber.tag(tag).d(message, *args)
        }
    }
    
    /**
     * Log info message
     */
    fun i(tag: String, message: String, vararg args: Any) {
        if (shouldLog(tag, LogLevel.INFO)) {
            Timber.tag(tag).i(message, *args)
        }
    }
    
    /**
     * Log warning message
     */
    fun w(tag: String, message: String, vararg args: Any) {
        if (shouldLog(tag, LogLevel.WARN)) {
            Timber.tag(tag).w(message, *args)
        }
    }
    
    /**
     * Log error message
     */
    fun e(tag: String, message: String, throwable: Throwable? = null, vararg args: Any) {
        if (shouldLog(tag, LogLevel.ERROR)) {
            if (throwable != null) {
                Timber.tag(tag).e(throwable, message, *args)
            } else {
                Timber.tag(tag).e(message, *args)
            }
        }
    }
    
    /**
     * Log XR-specific events
     */
    fun xr(event: XREvent) {
        val tag = "XR_${event.category}"
        val message = buildXRMessage(event)
        
        when (event.level) {
            LogLevel.VERBOSE -> v(tag, message)
            LogLevel.DEBUG -> d(tag, message)
            LogLevel.INFO -> i(tag, message)
            LogLevel.WARN -> w(tag, message)
            LogLevel.ERROR -> e(tag, message)
            LogLevel.NONE -> { /* Skip */ }
        }
        
        // Log to performance tree if applicable
        if (event.metrics != null) {
            performanceTree?.logMetrics(event.metrics)
        }
    }
    
    /**
     * Log performance metrics
     */
    fun performance(metric: PerformanceMetric) {
        performanceTree?.logMetric(metric)
        
        // Also log to standard output in debug
        d("PERF_${metric.category}", 
            "${metric.name}: ${metric.value}${metric.unit} " +
            "(min: ${metric.min}, max: ${metric.max}, avg: ${metric.average})")
    }
    
    /**
     * Log A2A communication
     */
    fun a2a(direction: String, agent: String, message: String) {
        val tag = "A2A_${direction.uppercase()}"
        i(tag, "[$agent] $message")
    }
    
    /**
     * Enable/disable logging for specific tags
     */
    fun setTagEnabled(tag: String, enabled: Boolean) {
        logTags[tag] = enabled
    }
    
    /**
     * Set global minimum log level
     */
    fun setMinLogLevel(level: LogLevel) {
        globalLogLevel = level
        Timber.i("Global log level set to: $level")
    }
    
    /**
     * Export logs to specified directory
     */
    fun exportLogs(exportDir: java.io.File): Boolean {
        return fileLoggingTree?.exportLogs(exportDir) ?: false
    }
    
    /**
     * Clear all log files
     */
    fun clearLogs() {
        fileLoggingTree?.clearLogs()
    }
    
    /**
     * Get current log files
     */
    fun getLogFiles(): List<java.io.File> {
        return fileLoggingTree?.getLogFiles() ?: emptyList()
    }
    
    /**
     * Cleanup and release resources
     */
    fun cleanup() {
        fileLoggingTree?.cleanup()
        performanceTree?.cleanup()
        TimberConfiguration.cleanup()
        isInitialized = false
    }
    
    /**
     * Check if logging should occur for tag and level
     */
    private fun shouldLog(tag: String, level: LogLevel): Boolean {
        // Check if tag is explicitly disabled
        if (logTags[tag] == false) {
            return false
        }
        
        // Check global log level
        return level.priority >= globalLogLevel.priority
    }
    
    /**
     * Build XR event message
     */
    private fun buildXRMessage(event: XREvent): String {
        val builder = StringBuilder()
        builder.append("[${event.eventType}] ")
        builder.append(event.message)
        
        event.metadata?.forEach { (key, value) ->
            builder.append(" | $key: $value")
        }
        
        return builder.toString()
    }
    
    /**
     * Configuration for logging system
     */
    data class LogConfig(
        val isDebug: Boolean = true,
        val enableFileLogging: Boolean = true,
        val enablePerformanceLogging: Boolean = true,
        val maxFileSize: Long = 10 * 1024 * 1024, // 10MB
        val maxFileCount: Int = 5,
        val minLogLevel: LogLevel = LogLevel.DEBUG
    )
    
    /**
     * XR-specific event data
     */
    data class XREvent(
        val category: String,
        val eventType: String,
        val message: String,
        val level: LogLevel = LogLevel.INFO,
        val metadata: Map<String, Any>? = null,
        val metrics: PerformanceMetric? = null
    )
    
    /**
     * Performance metric data
     */
    data class PerformanceMetric(
        val category: String,
        val name: String,
        val value: Double,
        val unit: String = "",
        val min: Double? = null,
        val max: Double? = null,
        val average: Double? = null,
        val timestamp: Long = System.currentTimeMillis()
    )
}