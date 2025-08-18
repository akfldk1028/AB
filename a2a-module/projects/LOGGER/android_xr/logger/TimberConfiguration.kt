package com.xr.logger

import android.content.Context
import android.util.Log
import timber.log.Timber
import java.io.File

/**
 * Timber logging configuration for Android XR applications
 * Handles initialization and setup of various logging trees
 */
class TimberConfiguration(private val context: Context) {
    
    companion object {
        private const val TAG = "XRLogger"
        private var isInitialized = false
        
        /**
         * Initialize Timber with appropriate trees based on build config
         */
        @JvmStatic
        fun initialize(context: Context, isDebug: Boolean = true) {
            if (isInitialized) {
                Timber.w("Timber already initialized")
                return
            }
            
            val config = TimberConfiguration(context)
            
            if (isDebug) {
                // Debug build - use enhanced debug tree
                Timber.plant(config.createDebugTree())
            } else {
                // Release build - use crash reporting tree
                Timber.plant(config.createReleaseTree())
            }
            
            // Always plant file logging tree for persistent logs
            Timber.plant(config.createFileLoggingTree())
            
            // Plant XR-specific performance tree
            Timber.plant(config.createPerformanceTree())
            
            isInitialized = true
            Timber.i("Timber initialized for Android XR logging")
        }
        
        /**
         * Clean up and release resources
         */
        @JvmStatic
        fun cleanup() {
            Timber.uprootAll()
            isInitialized = false
        }
    }
    
    /**
     * Create enhanced debug tree with XR-specific formatting
     */
    fun createDebugTree(): Timber.DebugTree {
        return XRDebugTree()
    }
    
    /**
     * Create release tree for crash reporting and analytics
     */
    fun createReleaseTree(): Timber.Tree {
        return ReleaseTree()
    }
    
    /**
     * Create file logging tree for persistent storage
     */
    fun createFileLoggingTree(): Timber.Tree {
        val logDir = File(context.filesDir, "logs")
        if (!logDir.exists()) {
            logDir.mkdirs()
        }
        return FileLoggingTree(logDir)
    }
    
    /**
     * Create performance monitoring tree for XR metrics
     */
    fun createPerformanceTree(): Timber.Tree {
        return PerformanceLoggingTree()
    }
    
    /**
     * Enhanced debug tree with XR-specific information
     */
    private class XRDebugTree : Timber.DebugTree() {
        override fun createStackElementTag(element: StackTraceElement): String {
            return String.format(
                "[XR:%s:%s:%s]",
                super.createStackElementTag(element),
                element.methodName,
                element.lineNumber
            )
        }
        
        override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
            val timestamp = System.currentTimeMillis()
            val threadName = Thread.currentThread().name
            val enhancedMessage = "[$threadName @$timestamp] $message"
            super.log(priority, tag, enhancedMessage, t)
        }
    }
    
    /**
     * Release tree for production logging
     */
    private class ReleaseTree : Timber.Tree() {
        override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
            // Only log warnings and above in release
            if (priority < Log.WARN) {
                return
            }
            
            // Log to crash reporting service
            when (priority) {
                Log.WARN -> logWarning(tag, message)
                Log.ERROR -> logError(tag, message, t)
                Log.ASSERT -> logFatal(tag, message, t)
            }
        }
        
        private fun logWarning(tag: String?, message: String) {
            // TODO: Send to crash reporting service
            Log.w(tag ?: TAG, message)
        }
        
        private fun logError(tag: String?, message: String, t: Throwable?) {
            // TODO: Send to crash reporting service
            Log.e(tag ?: TAG, message, t)
        }
        
        private fun logFatal(tag: String?, message: String, t: Throwable?) {
            // TODO: Send to crash reporting service
            Log.wtf(tag ?: TAG, message, t)
        }
    }
}