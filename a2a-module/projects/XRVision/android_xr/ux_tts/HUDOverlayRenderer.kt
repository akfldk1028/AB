package com.xrvision.android_xr.ux_tts

import android.content.Context
import android.graphics.*
import android.view.View
import kotlin.math.min

/**
 * HUD Overlay Renderer for Android XR Vision Analysis Results
 * Displays detected objects with confidence scores in an immersive XR environment
 */
class HUDOverlayRenderer(context: Context) : View(context) {
    
    // Vision analysis data
    data class DetectedObject(
        val label: String,
        val confidence: Float,
        val boundingBox: RectF? = null,
        val position: PointF? = null
    )
    
    private var detectedObjects = mutableListOf<DetectedObject>()
    private var displayMode = DisplayMode.MINIMAL
    
    // Paint objects for rendering
    private val hudPaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.FILL_AND_STROKE
        strokeWidth = 2f
    }
    
    private val textPaint = Paint().apply {
        isAntiAlias = true
        textSize = 24f
        typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL)
    }
    
    private val backgroundPaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.FILL
    }
    
    private val confidencePaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.FILL
        strokeWidth = 4f
    }
    
    // Display modes
    enum class DisplayMode {
        MINIMAL,      // Just labels and confidence
        DETAILED,     // Include bounding boxes
        FULL         // Include tracking lines and additional info
    }
    
    // Color scheme for XR visibility
    private object ColorScheme {
        const val PRIMARY = 0xE600FF00.toInt()      // Bright green with high opacity
        const val SECONDARY = 0xE6FFFFFF.toInt()    // White with high opacity
        const val BACKGROUND = 0x66000000.toInt()   // Semi-transparent black
        const val HIGH_CONFIDENCE = 0xE600FF00.toInt()  // Green for high confidence
        const val MED_CONFIDENCE = 0xE6FFFF00.toInt()   // Yellow for medium confidence
        const val LOW_CONFIDENCE = 0xE6FF0000.toInt()   // Red for low confidence
        const val CROSSHAIR = 0xCCFFFFFF.toInt()        // Semi-transparent white
    }
    
    /**
     * Update the vision analysis results for display
     */
    fun updateVisionResults(objects: List<String>, confidences: List<Float>) {
        detectedObjects.clear()
        objects.forEachIndexed { index, obj ->
            val confidence = confidences.getOrNull(index) ?: 0f
            detectedObjects.add(DetectedObject(obj, confidence))
        }
        invalidate() // Trigger redraw
    }
    
    /**
     * Update with detailed object information including bounding boxes
     */
    fun updateDetailedResults(objects: List<DetectedObject>) {
        detectedObjects.clear()
        detectedObjects.addAll(objects)
        invalidate()
    }
    
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        // Draw crosshair at center
        drawCrosshair(canvas)
        
        // Draw detected objects overlay
        when (displayMode) {
            DisplayMode.MINIMAL -> drawMinimalOverlay(canvas)
            DisplayMode.DETAILED -> drawDetailedOverlay(canvas)
            DisplayMode.FULL -> drawFullOverlay(canvas)
        }
        
        // Draw status indicators
        drawStatusIndicators(canvas)
    }
    
    private fun drawCrosshair(canvas: Canvas) {
        val centerX = width / 2f
        val centerY = height / 2f
        val crosshairSize = 30f
        
        hudPaint.color = ColorScheme.CROSSHAIR
        hudPaint.strokeWidth = 2f
        
        // Horizontal line
        canvas.drawLine(
            centerX - crosshairSize, centerY,
            centerX + crosshairSize, centerY,
            hudPaint
        )
        
        // Vertical line
        canvas.drawLine(
            centerX, centerY - crosshairSize,
            centerX, centerY + crosshairSize,
            hudPaint
        )
        
        // Center dot
        hudPaint.style = Paint.Style.FILL
        canvas.drawCircle(centerX, centerY, 3f, hudPaint)
        hudPaint.style = Paint.Style.FILL_AND_STROKE
    }
    
    private fun drawMinimalOverlay(canvas: Canvas) {
        if (detectedObjects.isEmpty()) return
        
        val startY = 100f
        val lineHeight = 40f
        var currentY = startY
        
        detectedObjects.forEach { obj ->
            drawObjectLabel(canvas, obj, 50f, currentY)
            currentY += lineHeight
        }
    }
    
    private fun drawDetailedOverlay(canvas: Canvas) {
        detectedObjects.forEach { obj ->
            // Draw bounding box if available
            obj.boundingBox?.let { box ->
                drawBoundingBox(canvas, box, obj.confidence)
            }
            
            // Draw label at position or default location
            val position = obj.position ?: PointF(50f, 100f)
            drawObjectLabel(canvas, obj, position.x, position.y)
        }
    }
    
    private fun drawFullOverlay(canvas: Canvas) {
        // Draw detailed overlay first
        drawDetailedOverlay(canvas)
        
        // Add tracking lines from center to objects
        val centerX = width / 2f
        val centerY = height / 2f
        
        detectedObjects.forEach { obj ->
            obj.position?.let { pos ->
                drawTrackingLine(canvas, centerX, centerY, pos.x, pos.y, obj.confidence)
            }
        }
        
        // Draw information panel
        drawInfoPanel(canvas)
    }
    
    private fun drawObjectLabel(canvas: Canvas, obj: DetectedObject, x: Float, y: Float) {
        // Background for text readability
        val text = "${obj.label} (${(obj.confidence * 100).toInt()}%)"
        val textBounds = Rect()
        textPaint.getTextBounds(text, 0, text.length, textBounds)
        
        val padding = 10f
        val bgRect = RectF(
            x - padding,
            y - textBounds.height() - padding,
            x + textBounds.width() + padding,
            y + padding
        )
        
        backgroundPaint.color = ColorScheme.BACKGROUND
        canvas.drawRoundRect(bgRect, 5f, 5f, backgroundPaint)
        
        // Text with confidence-based color
        textPaint.color = getConfidenceColor(obj.confidence)
        canvas.drawText(text, x, y, textPaint)
        
        // Confidence indicator bar
        drawConfidenceBar(canvas, x, y + 10f, obj.confidence)
    }
    
    private fun drawBoundingBox(canvas: Canvas, box: RectF, confidence: Float) {
        hudPaint.color = getConfidenceColor(confidence)
        hudPaint.style = Paint.Style.STROKE
        hudPaint.strokeWidth = 3f
        
        // Draw rounded rectangle for smoother appearance
        canvas.drawRoundRect(box, 10f, 10f, hudPaint)
        
        // Draw corner indicators for emphasis
        val cornerLength = 20f
        hudPaint.strokeWidth = 4f
        
        // Top-left corner
        canvas.drawLine(box.left, box.top, box.left + cornerLength, box.top, hudPaint)
        canvas.drawLine(box.left, box.top, box.left, box.top + cornerLength, hudPaint)
        
        // Top-right corner
        canvas.drawLine(box.right - cornerLength, box.top, box.right, box.top, hudPaint)
        canvas.drawLine(box.right, box.top, box.right, box.top + cornerLength, hudPaint)
        
        // Bottom-left corner
        canvas.drawLine(box.left, box.bottom - cornerLength, box.left, box.bottom, hudPaint)
        canvas.drawLine(box.left, box.bottom, box.left + cornerLength, box.bottom, hudPaint)
        
        // Bottom-right corner
        canvas.drawLine(box.right - cornerLength, box.bottom, box.right, box.bottom, hudPaint)
        canvas.drawLine(box.right, box.bottom - cornerLength, box.right, box.bottom, hudPaint)
    }
    
    private fun drawTrackingLine(canvas: Canvas, x1: Float, y1: Float, x2: Float, y2: Float, confidence: Float) {
        val paint = Paint().apply {
            color = getConfidenceColor(confidence)
            strokeWidth = 1f
            pathEffect = DashPathEffect(floatArrayOf(10f, 5f), 0f)
            isAntiAlias = true
        }
        
        canvas.drawLine(x1, y1, x2, y2, paint)
    }
    
    private fun drawConfidenceBar(canvas: Canvas, x: Float, y: Float, confidence: Float) {
        val barWidth = 100f
        val barHeight = 4f
        
        // Background bar
        backgroundPaint.color = 0x33FFFFFF
        canvas.drawRect(x, y, x + barWidth, y + barHeight, backgroundPaint)
        
        // Confidence fill
        confidencePaint.color = getConfidenceColor(confidence)
        canvas.drawRect(x, y, x + (barWidth * confidence), y + barHeight, confidencePaint)
    }
    
    private fun drawStatusIndicators(canvas: Canvas) {
        val indicatorX = width - 150f
        val indicatorY = 50f
        
        // Processing status
        val statusText = "VISION ACTIVE"
        textPaint.color = ColorScheme.PRIMARY
        textPaint.textSize = 18f
        canvas.drawText(statusText, indicatorX, indicatorY, textPaint)
        
        // Object count
        val countText = "Objects: ${detectedObjects.size}"
        textPaint.color = ColorScheme.SECONDARY
        canvas.drawText(countText, indicatorX, indicatorY + 25f, textPaint)
        
        // Average confidence
        if (detectedObjects.isNotEmpty()) {
            val avgConfidence = detectedObjects.map { it.confidence }.average()
            val avgText = "Avg: ${(avgConfidence * 100).toInt()}%"
            textPaint.color = getConfidenceColor(avgConfidence.toFloat())
            canvas.drawText(avgText, indicatorX, indicatorY + 50f, textPaint)
        }
    }
    
    private fun drawInfoPanel(canvas: Canvas) {
        val panelX = 50f
        val panelY = height - 200f
        val panelWidth = 300f
        val panelHeight = 150f
        
        // Panel background
        backgroundPaint.color = ColorScheme.BACKGROUND
        val panelRect = RectF(panelX, panelY, panelX + panelWidth, panelY + panelHeight)
        canvas.drawRoundRect(panelRect, 10f, 10f, backgroundPaint)
        
        // Panel content
        textPaint.color = ColorScheme.SECONDARY
        textPaint.textSize = 16f
        
        var textY = panelY + 30f
        canvas.drawText("Vision Analysis", panelX + 10f, textY, textPaint)
        
        textY += 30f
        detectedObjects.take(3).forEach { obj ->
            val infoText = "• ${obj.label}: ${(obj.confidence * 100).toInt()}%"
            canvas.drawText(infoText, panelX + 10f, textY, textPaint)
            textY += 25f
        }
    }
    
    private fun getConfidenceColor(confidence: Float): Int {
        return when {
            confidence >= 0.8f -> ColorScheme.HIGH_CONFIDENCE
            confidence >= 0.5f -> ColorScheme.MED_CONFIDENCE
            else -> ColorScheme.LOW_CONFIDENCE
        }
    }
    
    /**
     * Set the display mode for the HUD
     */
    fun setDisplayMode(mode: DisplayMode) {
        displayMode = mode
        invalidate()
    }
    
    /**
     * Clear all displayed objects
     */
    fun clearDisplay() {
        detectedObjects.clear()
        invalidate()
    }
    
    /**
     * Get current detected objects for TTS processing
     */
    fun getDetectedObjectsForTTS(): String {
        if (detectedObjects.isEmpty()) {
            return "No objects detected"
        }
        
        return detectedObjects.joinToString(", ") { obj ->
            "${obj.label} with ${(obj.confidence * 100).toInt()} percent confidence"
        }
    }
}