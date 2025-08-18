package com.xr.logger

import android.util.Log
import timber.log.Timber
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/**
 * File-based logging tree for persistent XR application logs
 * Supports log rotation, compression, and structured formatting
 */
class FileLoggingTree(
    private val logDirectory: File,
    private val maxFileSize: Long = 10 * 1024 * 1024, // 10MB default
    private val maxFileCount: Int = 5,
    private val logFilePrefix: String = "xr_log"
) : Timber.Tree() {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)
    private val fileNameDateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US)
    private val executor = Executors.newSingleThreadExecutor { r ->
        Thread(r, "FileLoggingTree-Writer").apply {
            isDaemon = true
            priority = Thread.MIN_PRIORITY
        }
    }
    
    private var currentLogFile: File? = null
    private var currentFileWriter: FileWriter? = null
    private val logBuffer = mutableListOf<LogEntry>()
    private val bufferLock = Any()
    private var bufferFlushTask: Runnable? = null
    
    companion object {
        private const val BUFFER_SIZE = 100
        private const val FLUSH_INTERVAL_MS = 5000L
    }
    
    init {
        createNewLogFile()
        schedulePeriodicFlush()
    }
    
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        val logEntry = LogEntry(
            timestamp = System.currentTimeMillis(),
            priority = priority,
            tag = tag ?: "XR",
            message = message,
            throwable = t,
            threadName = Thread.currentThread().name
        )
        
        synchronized(bufferLock) {
            logBuffer.add(logEntry)
            
            if (logBuffer.size >= BUFFER_SIZE) {
                flushBuffer()
            }
        }
    }
    
    /**
     * Create a new log file with timestamp
     */
    private fun createNewLogFile() {
        executor.execute {
            try {
                val timestamp = fileNameDateFormat.format(Date())
                val fileName = "${logFilePrefix}_$timestamp.log"
                currentLogFile = File(logDirectory, fileName)
                currentFileWriter?.close()
                currentFileWriter = FileWriter(currentLogFile, true)
                
                // Write header
                currentFileWriter?.apply {
                    write("=== Android XR Log File ===\n")
                    write("Created: ${dateFormat.format(Date())}\n")
                    write("Device: ${android.os.Build.MODEL}\n")
                    write("Android Version: ${android.os.Build.VERSION.RELEASE}\n")
                    write("===========================\n\n")
                    flush()
                }
                
                // Clean up old files
                rotateLogFiles()
            } catch (e: IOException) {
                Log.e("FileLoggingTree", "Failed to create log file", e)
            }
        }
    }
    
    /**
     * Flush buffered logs to file
     */
    private fun flushBuffer() {
        executor.execute {
            val logsToWrite = synchronized(bufferLock) {
                val logs = ArrayList(logBuffer)
                logBuffer.clear()
                logs
            }
            
            try {
                currentFileWriter?.let { writer ->
                    for (entry in logsToWrite) {
                        writer.write(formatLogEntry(entry))
                        writer.write("\n")
                    }
                    writer.flush()
                    
                    // Check if rotation needed
                    currentLogFile?.let { file ->
                        if (file.length() >= maxFileSize) {
                            createNewLogFile()
                        }
                    }
                }
            } catch (e: IOException) {
                Log.e("FileLoggingTree", "Failed to write logs to file", e)
            }
        }
    }
    
    /**
     * Format log entry for file output
     */
    private fun formatLogEntry(entry: LogEntry): String {
        val priorityChar = when (entry.priority) {
            Log.VERBOSE -> 'V'
            Log.DEBUG -> 'D'
            Log.INFO -> 'I'
            Log.WARN -> 'W'
            Log.ERROR -> 'E'
            Log.ASSERT -> 'A'
            else -> '?'
        }
        
        val timestamp = dateFormat.format(Date(entry.timestamp))
        val throwableInfo = entry.throwable?.let { 
            "\n${Log.getStackTraceString(it)}" 
        } ?: ""
        
        return String.format(
            "%s %c/[%s] %s: %s%s",
            timestamp,
            priorityChar,
            entry.threadName,
            entry.tag,
            entry.message,
            throwableInfo
        )
    }
    
    /**
     * Rotate log files, keeping only the most recent ones
     */
    private fun rotateLogFiles() {
        try {
            val logFiles = logDirectory.listFiles { file ->
                file.name.startsWith(logFilePrefix) && file.name.endsWith(".log")
            }?.sortedByDescending { it.lastModified() } ?: return
            
            // Delete old files beyond max count
            if (logFiles.size > maxFileCount) {
                logFiles.subList(maxFileCount, logFiles.size).forEach { file ->
                    file.delete()
                }
            }
        } catch (e: Exception) {
            Log.e("FileLoggingTree", "Failed to rotate log files", e)
        }
    }
    
    /**
     * Schedule periodic buffer flush
     */
    private fun schedulePeriodicFlush() {
        bufferFlushTask = Runnable {
            synchronized(bufferLock) {
                if (logBuffer.isNotEmpty()) {
                    flushBuffer()
                }
            }
        }
        
        Executors.newSingleThreadScheduledExecutor().scheduleWithFixedDelay(
            bufferFlushTask,
            FLUSH_INTERVAL_MS,
            FLUSH_INTERVAL_MS,
            TimeUnit.MILLISECONDS
        )
    }
    
    /**
     * Get all log files
     */
    fun getLogFiles(): List<File> {
        return logDirectory.listFiles { file ->
            file.name.startsWith(logFilePrefix) && file.name.endsWith(".log")
        }?.sortedByDescending { it.lastModified() } ?: emptyList()
    }
    
    /**
     * Export logs to specified directory
     */
    fun exportLogs(exportDirectory: File): Boolean {
        return try {
            flushBuffer() // Ensure all logs are written
            
            val logFiles = getLogFiles()
            logFiles.forEach { logFile ->
                val exportFile = File(exportDirectory, logFile.name)
                logFile.copyTo(exportFile, overwrite = true)
            }
            true
        } catch (e: Exception) {
            Log.e("FileLoggingTree", "Failed to export logs", e)
            false
        }
    }
    
    /**
     * Clear all log files
     */
    fun clearLogs() {
        executor.execute {
            try {
                currentFileWriter?.close()
                getLogFiles().forEach { it.delete() }
                createNewLogFile()
            } catch (e: Exception) {
                Log.e("FileLoggingTree", "Failed to clear logs", e)
            }
        }
    }
    
    /**
     * Clean up resources
     */
    fun cleanup() {
        synchronized(bufferLock) {
            flushBuffer()
        }
        currentFileWriter?.close()
        executor.shutdown()
    }
    
    /**
     * Data class for log entries
     */
    private data class LogEntry(
        val timestamp: Long,
        val priority: Int,
        val tag: String,
        val message: String,
        val throwable: Throwable?,
        val threadName: String
    )
}