package com.xr.logger

import android.util.Log
import timber.log.Timber
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong

/**
 * Performance-focused logging tree for XR metrics
 * Tracks frame rates, latency, memory usage, and other performance indicators
 */
class PerformanceLoggingTree : Timber.Tree() {
    
    private val metricsMap = ConcurrentHashMap<String, MetricTracker>()
    private val sessionStartTime = System.currentTimeMillis()
    private val executor = Executors.newSingleThreadScheduledExecutor { r ->
        Thread(r, "PerformanceLogger").apply {
            isDaemon = true
            priority = Thread.MIN_PRIORITY
        }
    }
    
    companion object {
        private const val TAG = "XR_PERF"
        private const val METRICS_REPORT_INTERVAL = 30000L // 30 seconds
        
        // Standard XR metrics categories
        const val CATEGORY_FRAME = "FRAME"
        const val CATEGORY_MEMORY = "MEMORY"
        const val CATEGORY_LATENCY = "LATENCY"
        const val CATEGORY_AI = "AI"
        const val CATEGORY_CAMERA = "CAMERA"
        const val CATEGORY_NETWORK = "NETWORK"
        const val CATEGORY_BATTERY = "BATTERY"
        const val CATEGORY_THERMAL = "THERMAL"
    }
    
    init {
        // Schedule periodic metrics reporting
        executor.scheduleWithFixedDelay(
            ::reportMetrics,
            METRICS_REPORT_INTERVAL,
            METRICS_REPORT_INTERVAL,
            TimeUnit.MILLISECONDS
        )
    }
    
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        // Parse performance-related messages
        if (tag?.startsWith("PERF_") == true || tag == TAG) {
            parseAndTrackMetric(message)
        }
        
        // Forward to standard logging if needed
        if (priority >= Log.INFO) {
            Log.println(priority, tag ?: TAG, message)
        }
    }
    
    /**
     * Log a performance metric
     */
    fun logMetric(metric: LoggerManager.PerformanceMetric) {
        val key = "${metric.category}_${metric.name}"
        val tracker = metricsMap.getOrPut(key) {
            MetricTracker(metric.category, metric.name, metric.unit)
        }
        tracker.addValue(metric.value)
        
        // Check for performance issues
        checkPerformanceThresholds(metric)
    }
    
    /**
     * Log multiple metrics at once
     */
    fun logMetrics(metrics: LoggerManager.PerformanceMetric) {
        logMetric(metrics)
    }
    
    /**
     * Track frame timing
     */
    fun frameStart(frameId: Long) {
        val key = "frame_$frameId"
        metricsMap[key] = MetricTracker(CATEGORY_FRAME, "frame_time", "ms").apply {
            frameStartTime = System.nanoTime()
        }
    }
    
    /**
     * Complete frame timing
     */
    fun frameEnd(frameId: Long) {
        val key = "frame_$frameId"
        metricsMap[key]?.let { tracker ->
            val duration = (System.nanoTime() - tracker.frameStartTime) / 1_000_000.0 // Convert to ms
            
            // Track frame time
            val frameMetric = metricsMap.getOrPut("${CATEGORY_FRAME}_time") {
                MetricTracker(CATEGORY_FRAME, "time", "ms")
            }
            frameMetric.addValue(duration)
            
            // Calculate FPS
            val fps = if (duration > 0) 1000.0 / duration else 0.0
            val fpsMetric = metricsMap.getOrPut("${CATEGORY_FRAME}_fps") {
                MetricTracker(CATEGORY_FRAME, "fps", "fps")
            }
            fpsMetric.addValue(fps)
            
            // Remove temporary frame tracker
            metricsMap.remove(key)
            
            // Log if frame dropped (>16.67ms for 60fps)
            if (duration > 16.67) {
                Timber.tag(TAG).w("Frame drop detected: %.2fms (%.1f fps)", duration, fps)
            }
        }
    }
    
    /**
     * Track memory usage
     */
    fun trackMemory() {
        val runtime = Runtime.getRuntime()
        val totalMemory = runtime.totalMemory() / (1024.0 * 1024.0) // MB
        val freeMemory = runtime.freeMemory() / (1024.0 * 1024.0) // MB
        val usedMemory = totalMemory - freeMemory
        
        logMetric(LoggerManager.PerformanceMetric(
            category = CATEGORY_MEMORY,
            name = "used",
            value = usedMemory,
            unit = "MB"
        ))
        
        logMetric(LoggerManager.PerformanceMetric(
            category = CATEGORY_MEMORY,
            name = "free",
            value = freeMemory,
            unit = "MB"
        ))
    }
    
    /**
     * Track AI inference time
     */
    fun trackAIInference(modelName: String, inferenceTimeMs: Double) {
        logMetric(LoggerManager.PerformanceMetric(
            category = CATEGORY_AI,
            name = modelName,
            value = inferenceTimeMs,
            unit = "ms"
        ))
    }
    
    /**
     * Track camera processing
     */
    fun trackCameraFrame(processingTimeMs: Double) {
        logMetric(LoggerManager.PerformanceMetric(
            category = CATEGORY_CAMERA,
            name = "processing",
            value = processingTimeMs,
            unit = "ms"
        ))
    }
    
    /**
     * Get current metrics summary
     */
    fun getMetricsSummary(): Map<String, MetricSummary> {
        return metricsMap.mapValues { (_, tracker) ->
            tracker.getSummary()
        }
    }
    
    /**
     * Parse metric from log message
     */
    private fun parseAndTrackMetric(message: String) {
        // Try to parse structured metric format: "METRIC_NAME: value unit"
        val regex = Regex("([A-Z_]+): ([0-9.]+)\\s*(\\w*)")
        regex.find(message)?.let { match ->
            val name = match.groupValues[1]
            val value = match.groupValues[2].toDoubleOrNull() ?: return
            val unit = match.groupValues[3].ifEmpty { "" }
            
            val category = when {
                name.contains("FPS") || name.contains("FRAME") -> CATEGORY_FRAME
                name.contains("MEMORY") || name.contains("MEM") -> CATEGORY_MEMORY
                name.contains("LATENCY") || name.contains("LAT") -> CATEGORY_LATENCY
                name.contains("AI") || name.contains("INFERENCE") -> CATEGORY_AI
                else -> "GENERAL"
            }
            
            logMetric(LoggerManager.PerformanceMetric(
                category = category,
                name = name,
                value = value,
                unit = unit
            ))
        }
    }
    
    /**
     * Check performance thresholds and log warnings
     */
    private fun checkPerformanceThresholds(metric: LoggerManager.PerformanceMetric) {
        when (metric.category) {
            CATEGORY_FRAME -> {
                if (metric.name == "fps" && metric.value < 30) {
                    Timber.tag(TAG).w("Low FPS detected: %.1f fps", metric.value)
                }
            }
            CATEGORY_MEMORY -> {
                if (metric.name == "used" && metric.value > 500) {
                    Timber.tag(TAG).w("High memory usage: %.1f MB", metric.value)
                }
            }
            CATEGORY_LATENCY -> {
                if (metric.value > 100) {
                    Timber.tag(TAG).w("High latency detected: %.1f ms", metric.value)
                }
            }
            CATEGORY_AI -> {
                if (metric.value > 500) {
                    Timber.tag(TAG).w("Slow AI inference: %.1f ms for %s", metric.value, metric.name)
                }
            }
        }
    }
    
    /**
     * Report aggregated metrics
     */
    private fun reportMetrics() {
        val sessionDuration = (System.currentTimeMillis() - sessionStartTime) / 1000.0 / 60.0 // minutes
        
        Timber.tag(TAG).i("=== Performance Report (Session: %.1f min) ===", sessionDuration)
        
        metricsMap.forEach { (key, tracker) ->
            val summary = tracker.getSummary()
            if (summary.count > 0) {
                Timber.tag(TAG).i(
                    "%s.%s: avg=%.2f%s, min=%.2f, max=%.2f, count=%d",
                    summary.category,
                    summary.name,
                    summary.average,
                    summary.unit,
                    summary.min,
                    summary.max,
                    summary.count
                )
            }
        }
        
        Timber.tag(TAG).i("===========================================")
    }
    
    /**
     * Clean up resources
     */
    fun cleanup() {
        reportMetrics() // Final report
        executor.shutdown()
        metricsMap.clear()
    }
    
    /**
     * Metric tracker for aggregating values
     */
    private class MetricTracker(
        val category: String,
        val name: String,
        val unit: String
    ) {
        private val count = AtomicLong(0)
        private val sum = java.util.concurrent.atomic.DoubleAdder()
        private var min = Double.MAX_VALUE
        private var max = Double.MIN_VALUE
        var frameStartTime: Long = 0L
        
        fun addValue(value: Double) {
            count.incrementAndGet()
            sum.add(value)
            synchronized(this) {
                min = minOf(min, value)
                max = maxOf(max, value)
            }
        }
        
        fun getSummary(): MetricSummary {
            val currentCount = count.get()
            val currentSum = sum.sum()
            
            return MetricSummary(
                category = category,
                name = name,
                unit = unit,
                count = currentCount,
                sum = currentSum,
                average = if (currentCount > 0) currentSum / currentCount else 0.0,
                min = if (min == Double.MAX_VALUE) 0.0 else min,
                max = if (max == Double.MIN_VALUE) 0.0 else max
            )
        }
    }
    
    /**
     * Metric summary data
     */
    data class MetricSummary(
        val category: String,
        val name: String,
        val unit: String,
        val count: Long,
        val sum: Double,
        val average: Double,
        val min: Double,
        val max: Double
    )
}