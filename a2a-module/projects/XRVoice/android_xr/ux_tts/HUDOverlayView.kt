package com.xrvoice.android_xr.ux_tts

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.util.Log
import android.view.View
import androidx.core.content.ContextCompat
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * Custom view for XR HUD overlay with crosshair and visual feedback
 * Manages rendering of all HUD elements in XR environment
 */
class HUDOverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {
    
    companion object {
        private const val TAG = "HUDOverlayView"
        private const val FPS_TARGET = 60
        private const val FRAME_TIME_MS = 1000L / FPS_TARGET
        private const val NOTIFICATION_DISPLAY_TIME = 3000L
        private const val STATUS_UPDATE_INTERVAL = 100L
    }
    
    // Rendering components
    private val crosshairRenderer = CrosshairRenderer()
    private val notificationQueue = ConcurrentLinkedQueue<NotificationItem>()
    private val statusIndicators = mutableMapOf<String, StatusIndicator>()
    
    // Render thread
    private val renderScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var renderJob: Job? = null
    
    // Display metrics
    private var viewWidth = 0
    private var viewHeight = 0
    private var centerX = 0f
    private var centerY = 0f
    private var scaleFactor = 1f
    
    // State management
    private val _isOverlayActive = MutableStateFlow(true)
    val isOverlayActive: StateFlow<Boolean> = _isOverlayActive
    
    private val _currentNotification = MutableStateFlow<NotificationItem?>(null)
    val currentNotification: StateFlow<NotificationItem?> = _currentNotification
    
    // Paint objects
    private val backgroundPaint = Paint().apply {
        color = Color.argb(20, 0, 0, 0)
        style = Paint.Style.FILL
    }
    
    private val textPaint = Paint().apply {
        color = Color.WHITE
        textSize = 16f * resources.displayMetrics.density
        isAntiAlias = true
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        setShadowLayer(2f, 1f, 1f, Color.BLACK)
    }
    
    private val notificationPaint = Paint().apply {
        color = Color.argb(200, 30, 30, 30)
        style = Paint.Style.FILL
        isAntiAlias = true
    }
    
    private val borderPaint = Paint().apply {
        color = Color.argb(100, 255, 255, 255)
        style = Paint.Style.STROKE
        strokeWidth = 2f
        isAntiAlias = true
    }
    
    private val statusPaint = Paint().apply {
        style = Paint.Style.FILL
        isAntiAlias = true
    }
    
    init {
        setLayerType(LAYER_TYPE_HARDWARE, null)
        setWillNotDraw(false)
        startRenderLoop()
    }
    
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        viewWidth = w
        viewHeight = h
        centerX = w / 2f
        centerY = h / 2f
        
        // Adjust scale for different screen sizes
        scaleFactor = minOf(w, h) / 1080f
        
        Log.d(TAG, "View size changed: ${w}x${h}, scale: $scaleFactor")
    }
    
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        if (!_isOverlayActive.value) return
        
        val currentTime = System.currentTimeMillis()
        
        // Clear background (optional semi-transparent overlay)
        // canvas.drawRect(0f, 0f, viewWidth.toFloat(), viewHeight.toFloat(), backgroundPaint)
        
        // Draw crosshair at center
        crosshairRenderer.render(canvas, centerX, centerY, currentTime)
        
        // Draw notifications
        drawNotifications(canvas, currentTime)
        
        // Draw status indicators
        drawStatusIndicators(canvas)
        
        // Draw additional HUD elements
        drawHUDElements(canvas)
    }
    
    private fun drawNotifications(canvas: Canvas, currentTime: Long) {
        // Process notification queue
        if (_currentNotification.value == null && notificationQueue.isNotEmpty()) {
            _currentNotification.value = notificationQueue.poll()
        }
        
        _currentNotification.value?.let { notification ->
            val elapsed = currentTime - notification.timestamp
            
            if (elapsed < NOTIFICATION_DISPLAY_TIME) {
                val alpha = if (elapsed < 300) {
                    // Fade in
                    (elapsed / 300f * 255).toInt()
                } else if (elapsed > NOTIFICATION_DISPLAY_TIME - 300) {
                    // Fade out
                    ((NOTIFICATION_DISPLAY_TIME - elapsed) / 300f * 255).toInt()
                } else {
                    255
                }
                
                drawNotificationBox(canvas, notification, alpha)
            } else {
                _currentNotification.value = null
            }
        }
    }
    
    private fun drawNotificationBox(canvas: Canvas, notification: NotificationItem, alpha: Int) {
        val padding = 20f * scaleFactor
        val cornerRadius = 10f * scaleFactor
        
        // Calculate text bounds
        val textBounds = Rect()
        textPaint.getTextBounds(notification.message, 0, notification.message.length, textBounds)
        
        val boxWidth = textBounds.width() + padding * 2
        val boxHeight = textBounds.height() + padding * 2
        
        val boxLeft = centerX - boxWidth / 2
        val boxTop = viewHeight * 0.15f // Position at 15% from top
        val boxRight = boxLeft + boxWidth
        val boxBottom = boxTop + boxHeight
        
        // Draw notification background
        notificationPaint.alpha = alpha
        val rectF = RectF(boxLeft, boxTop, boxRight, boxBottom)
        canvas.drawRoundRect(rectF, cornerRadius, cornerRadius, notificationPaint)
        
        // Draw border
        borderPaint.alpha = alpha / 2
        canvas.drawRoundRect(rectF, cornerRadius, cornerRadius, borderPaint)
        
        // Draw icon if present
        notification.icon?.let { icon ->
            val iconSize = boxHeight * 0.6f
            val iconLeft = boxLeft + padding
            val iconTop = boxTop + (boxHeight - iconSize) / 2
            
            val iconPaint = Paint().apply {
                this.alpha = alpha
            }
            
            // Draw icon placeholder (in real app, draw actual icon)
            canvas.drawCircle(
                iconLeft + iconSize / 2,
                iconTop + iconSize / 2,
                iconSize / 2,
                iconPaint
            )
        }
        
        // Draw text
        textPaint.alpha = alpha
        textPaint.color = when (notification.type) {
            NotificationType.SUCCESS -> Color.GREEN
            NotificationType.WARNING -> Color.YELLOW
            NotificationType.ERROR -> Color.RED
            NotificationType.INFO -> Color.WHITE
        }
        
        val textX = centerX
        val textY = boxTop + boxHeight / 2 + textBounds.height() / 2
        
        textPaint.textAlign = Paint.Align.CENTER
        canvas.drawText(notification.message, textX, textY, textPaint)
    }
    
    private fun drawStatusIndicators(canvas: Canvas) {
        val indicatorSize = 10f * scaleFactor
        val spacing = 20f * scaleFactor
        var offsetX = 50f * scaleFactor
        val offsetY = 50f * scaleFactor
        
        statusIndicators.forEach { (_, indicator) ->
            if (indicator.isVisible) {
                statusPaint.color = indicator.color
                
                when (indicator.shape) {
                    IndicatorShape.CIRCLE -> {
                        canvas.drawCircle(offsetX, offsetY, indicatorSize, statusPaint)
                    }
                    IndicatorShape.SQUARE -> {
                        canvas.drawRect(
                            offsetX - indicatorSize,
                            offsetY - indicatorSize,
                            offsetX + indicatorSize,
                            offsetY + indicatorSize,
                            statusPaint
                        )
                    }
                    IndicatorShape.TRIANGLE -> {
                        val path = Path().apply {
                            moveTo(offsetX, offsetY - indicatorSize)
                            lineTo(offsetX - indicatorSize, offsetY + indicatorSize)
                            lineTo(offsetX + indicatorSize, offsetY + indicatorSize)
                            close()
                        }
                        canvas.drawPath(path, statusPaint)
                    }
                }
                
                // Draw label
                textPaint.textSize = 12f * scaleFactor
                textPaint.color = Color.WHITE
                textPaint.alpha = 200
                textPaint.textAlign = Paint.Align.LEFT
                canvas.drawText(
                    indicator.label,
                    offsetX + indicatorSize + 5f,
                    offsetY + 5f,
                    textPaint
                )
                
                offsetX += indicatorSize * 2 + spacing + textPaint.measureText(indicator.label)
            }
        }
    }
    
    private fun drawHUDElements(canvas: Canvas) {
        // Draw compass (optional)
        drawCompass(canvas)
        
        // Draw distance indicator (optional)
        drawDistanceIndicator(canvas)
        
        // Draw connection status
        drawConnectionStatus(canvas)
    }
    
    private fun drawCompass(canvas: Canvas) {
        val compassRadius = 30f * scaleFactor
        val compassX = viewWidth - 80f * scaleFactor
        val compassY = 80f * scaleFactor
        
        // Draw compass circle
        borderPaint.alpha = 100
        canvas.drawCircle(compassX, compassY, compassRadius, borderPaint)
        
        // Draw N indicator
        textPaint.textSize = 14f * scaleFactor
        textPaint.color = Color.WHITE
        textPaint.alpha = 200
        textPaint.textAlign = Paint.Align.CENTER
        canvas.drawText("N", compassX, compassY - compassRadius - 10f, textPaint)
    }
    
    private fun drawDistanceIndicator(canvas: Canvas) {
        // Draw distance scale at bottom
        val scaleY = viewHeight - 100f * scaleFactor
        val scaleWidth = 200f * scaleFactor
        val scaleX = centerX - scaleWidth / 2
        
        borderPaint.alpha = 50
        canvas.drawLine(scaleX, scaleY, scaleX + scaleWidth, scaleY, borderPaint)
        
        // Draw scale marks
        for (i in 0..4) {
            val markX = scaleX + (scaleWidth / 4) * i
            canvas.drawLine(markX, scaleY - 5f, markX, scaleY + 5f, borderPaint)
        }
    }
    
    private fun drawConnectionStatus(canvas: Canvas) {
        val statusX = viewWidth - 50f * scaleFactor
        val statusY = viewHeight - 50f * scaleFactor
        
        // Draw connection indicator
        val connectionColor = if (isConnected()) Color.GREEN else Color.RED
        statusPaint.color = connectionColor
        statusPaint.alpha = 200
        
        canvas.drawCircle(statusX, statusY, 5f * scaleFactor, statusPaint)
    }
    
    private fun isConnected(): Boolean {
        // Check connection status (placeholder)
        return true
    }
    
    /**
     * Start continuous render loop
     */
    private fun startRenderLoop() {
        renderJob?.cancel()
        renderJob = renderScope.launch {
            while (isActive) {
                invalidate()
                delay(FRAME_TIME_MS)
            }
        }
    }
    
    /**
     * Stop render loop
     */
    private fun stopRenderLoop() {
        renderJob?.cancel()
        renderJob = null
    }
    
    /**
     * Show notification
     */
    fun showNotification(
        message: String,
        type: NotificationType = NotificationType.INFO,
        icon: Bitmap? = null
    ) {
        val notification = NotificationItem(
            message = message,
            type = type,
            icon = icon,
            timestamp = System.currentTimeMillis()
        )
        
        notificationQueue.offer(notification)
        Log.d(TAG, "Notification queued: $message")
    }
    
    /**
     * Add status indicator
     */
    fun addStatusIndicator(
        id: String,
        label: String,
        color: Int,
        shape: IndicatorShape = IndicatorShape.CIRCLE
    ) {
        statusIndicators[id] = StatusIndicator(label, color, shape, true)
    }
    
    /**
     * Update status indicator
     */
    fun updateStatusIndicator(id: String, color: Int? = null, isVisible: Boolean? = null) {
        statusIndicators[id]?.let { indicator ->
            color?.let { indicator.color = it }
            isVisible?.let { indicator.isVisible = it }
        }
    }
    
    /**
     * Remove status indicator
     */
    fun removeStatusIndicator(id: String) {
        statusIndicators.remove(id)
    }
    
    /**
     * Configure crosshair
     */
    fun configureCrosshair(style: CrosshairRenderer.CrosshairStyle) {
        crosshairRenderer.setStyle(style)
    }
    
    /**
     * Trigger crosshair feedback
     */
    fun triggerCrosshairFeedback(type: CrosshairRenderer.FeedbackType) {
        crosshairRenderer.triggerFeedback(type)
    }
    
    /**
     * Set crosshair active state
     */
    fun setCrosshairActive(active: Boolean) {
        crosshairRenderer.setActive(active)
    }
    
    /**
     * Set overlay visibility
     */
    fun setOverlayActive(active: Boolean) {
        _isOverlayActive.value = active
        if (active) {
            startRenderLoop()
        } else {
            stopRenderLoop()
        }
    }
    
    /**
     * Clean up resources
     */
    fun cleanup() {
        stopRenderLoop()
        renderScope.cancel()
        notificationQueue.clear()
        statusIndicators.clear()
    }
    
    // Data classes
    data class NotificationItem(
        val message: String,
        val type: NotificationType,
        val icon: Bitmap? = null,
        val timestamp: Long
    )
    
    enum class NotificationType {
        INFO, SUCCESS, WARNING, ERROR
    }
    
    data class StatusIndicator(
        val label: String,
        var color: Int,
        val shape: IndicatorShape,
        var isVisible: Boolean
    )
    
    enum class IndicatorShape {
        CIRCLE, SQUARE, TRIANGLE
    }
}