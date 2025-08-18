package com.xrvoice.android_xr.ux_tts

import android.graphics.*
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlin.math.*

/**
 * Renders crosshair and HUD elements for XR display
 * Provides various crosshair styles and dynamic feedback animations
 */
class CrosshairRenderer {
    
    companion object {
        private const val TAG = "CrosshairRenderer"
        private const val DEFAULT_SIZE = 50f
        private const val DEFAULT_THICKNESS = 3f
        private const val DEFAULT_GAP = 10f
        private const val ANIMATION_DURATION = 300L // milliseconds
        private const val PULSE_DURATION = 1000L
    }
    
    enum class CrosshairStyle {
        SIMPLE_CROSS,
        DOT,
        CIRCLE,
        DYNAMIC_CROSS,
        BRACKET,
        TRIANGULAR,
        CUSTOM
    }
    
    enum class FeedbackType {
        NONE,
        PULSE,
        SCALE,
        COLOR_CHANGE,
        ROTATION,
        HIT_MARKER
    }
    
    // Crosshair configuration
    private var style = CrosshairStyle.DYNAMIC_CROSS
    private var size = DEFAULT_SIZE
    private var thickness = DEFAULT_THICKNESS
    private var gap = DEFAULT_GAP
    private var baseColor = Color.WHITE
    private var activeColor = Color.GREEN
    private var errorColor = Color.RED
    private var currentColor = baseColor
    
    // Animation state
    private var animationStartTime = 0L
    private var currentFeedback = FeedbackType.NONE
    private var animationProgress = 0f
    private var rotationAngle = 0f
    private var pulseScale = 1f
    
    // State management
    private val _isVisible = MutableStateFlow(true)
    val isVisible: StateFlow<Boolean> = _isVisible
    
    private val _isActive = MutableStateFlow(false)
    val isActive: StateFlow<Boolean> = _isActive
    
    // Paint objects
    private val crosshairPaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }
    
    private val fillPaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.FILL
    }
    
    private val textPaint = Paint().apply {
        isAntiAlias = true
        textAlign = Paint.Align.CENTER
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
    }
    
    private val glowPaint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.STROKE
        maskFilter = BlurMaskFilter(8f, BlurMaskFilter.Blur.NORMAL)
    }
    
    /**
     * Render crosshair on canvas
     */
    fun render(canvas: Canvas, centerX: Float, centerY: Float, currentTime: Long) {
        if (!_isVisible.value) return
        
        // Update animation
        updateAnimation(currentTime)
        
        // Apply animation transforms
        canvas.save()
        canvas.translate(centerX, centerY)
        
        if (currentFeedback == FeedbackType.ROTATION) {
            canvas.rotate(rotationAngle)
        }
        
        if (currentFeedback == FeedbackType.SCALE || currentFeedback == FeedbackType.PULSE) {
            canvas.scale(pulseScale, pulseScale)
        }
        
        // Draw based on style
        when (style) {
            CrosshairStyle.SIMPLE_CROSS -> drawSimpleCross(canvas)
            CrosshairStyle.DOT -> drawDot(canvas)
            CrosshairStyle.CIRCLE -> drawCircle(canvas)
            CrosshairStyle.DYNAMIC_CROSS -> drawDynamicCross(canvas)
            CrosshairStyle.BRACKET -> drawBracket(canvas)
            CrosshairStyle.TRIANGULAR -> drawTriangular(canvas)
            CrosshairStyle.CUSTOM -> drawCustom(canvas)
        }
        
        // Draw feedback overlay
        if (currentFeedback == FeedbackType.HIT_MARKER) {
            drawHitMarker(canvas)
        }
        
        canvas.restore()
    }
    
    private fun drawSimpleCross(canvas: Canvas) {
        crosshairPaint.color = currentColor
        crosshairPaint.strokeWidth = thickness
        
        // Horizontal line
        canvas.drawLine(-size / 2, 0f, -gap / 2, 0f, crosshairPaint)
        canvas.drawLine(gap / 2, 0f, size / 2, 0f, crosshairPaint)
        
        // Vertical line
        canvas.drawLine(0f, -size / 2, 0f, -gap / 2, crosshairPaint)
        canvas.drawLine(0f, gap / 2, 0f, size / 2, crosshairPaint)
    }
    
    private fun drawDot(canvas: Canvas) {
        fillPaint.color = currentColor
        canvas.drawCircle(0f, 0f, thickness * 2, fillPaint)
        
        // Outer ring for visibility
        crosshairPaint.color = adjustAlpha(currentColor, 100)
        crosshairPaint.strokeWidth = thickness / 2
        canvas.drawCircle(0f, 0f, size / 3, crosshairPaint)
    }
    
    private fun drawCircle(canvas: Canvas) {
        crosshairPaint.color = currentColor
        crosshairPaint.strokeWidth = thickness
        
        // Main circle
        canvas.drawCircle(0f, 0f, size / 2, crosshairPaint)
        
        // Center dot
        fillPaint.color = currentColor
        canvas.drawCircle(0f, 0f, thickness, fillPaint)
    }
    
    private fun drawDynamicCross(canvas: Canvas) {
        crosshairPaint.color = currentColor
        crosshairPaint.strokeWidth = thickness
        
        // Draw with glow effect when active
        if (_isActive.value) {
            glowPaint.color = adjustAlpha(activeColor, 100)
            glowPaint.strokeWidth = thickness * 1.5f
            
            // Draw glow
            drawCrossLines(canvas, glowPaint, size * 0.6f, gap * 1.2f)
        }
        
        // Main cross
        drawCrossLines(canvas, crosshairPaint, size / 2, gap / 2)
        
        // Corner indicators
        val cornerOffset = size * 0.7f
        val cornerLength = size * 0.15f
        
        crosshairPaint.strokeWidth = thickness * 0.7f
        crosshairPaint.color = adjustAlpha(currentColor, 150)
        
        // Top-left
        canvas.drawLine(-cornerOffset, -cornerOffset, -cornerOffset + cornerLength, -cornerOffset, crosshairPaint)
        canvas.drawLine(-cornerOffset, -cornerOffset, -cornerOffset, -cornerOffset + cornerLength, crosshairPaint)
        
        // Top-right
        canvas.drawLine(cornerOffset, -cornerOffset, cornerOffset - cornerLength, -cornerOffset, crosshairPaint)
        canvas.drawLine(cornerOffset, -cornerOffset, cornerOffset, -cornerOffset + cornerLength, crosshairPaint)
        
        // Bottom-left
        canvas.drawLine(-cornerOffset, cornerOffset, -cornerOffset + cornerLength, cornerOffset, crosshairPaint)
        canvas.drawLine(-cornerOffset, cornerOffset, -cornerOffset, cornerOffset - cornerLength, crosshairPaint)
        
        // Bottom-right
        canvas.drawLine(cornerOffset, cornerOffset, cornerOffset - cornerLength, cornerOffset, crosshairPaint)
        canvas.drawLine(cornerOffset, cornerOffset, cornerOffset, cornerOffset - cornerLength, crosshairPaint)
    }
    
    private fun drawBracket(canvas: Canvas) {
        crosshairPaint.color = currentColor
        crosshairPaint.strokeWidth = thickness
        
        val bracketSize = size * 0.3f
        val bracketGap = size * 0.4f
        
        // Left bracket
        canvas.drawLine(-bracketGap, -bracketSize, -bracketGap, bracketSize, crosshairPaint)
        canvas.drawLine(-bracketGap, -bracketSize, -bracketGap + bracketSize/3, -bracketSize, crosshairPaint)
        canvas.drawLine(-bracketGap, bracketSize, -bracketGap + bracketSize/3, bracketSize, crosshairPaint)
        
        // Right bracket
        canvas.drawLine(bracketGap, -bracketSize, bracketGap, bracketSize, crosshairPaint)
        canvas.drawLine(bracketGap, -bracketSize, bracketGap - bracketSize/3, -bracketSize, crosshairPaint)
        canvas.drawLine(bracketGap, bracketSize, bracketGap - bracketSize/3, bracketSize, crosshairPaint)
        
        // Center dot
        fillPaint.color = currentColor
        canvas.drawCircle(0f, 0f, thickness, fillPaint)
    }
    
    private fun drawTriangular(canvas: Canvas) {
        crosshairPaint.color = currentColor
        crosshairPaint.strokeWidth = thickness
        
        val triangleSize = size * 0.4f
        val path = Path()
        
        // Top triangle
        path.moveTo(0f, -triangleSize)
        path.lineTo(-triangleSize/2, -triangleSize/2)
        path.lineTo(triangleSize/2, -triangleSize/2)
        path.close()
        
        canvas.drawPath(path, crosshairPaint)
        
        // Center dot
        fillPaint.color = currentColor
        canvas.drawCircle(0f, 0f, thickness * 1.5f, fillPaint)
    }
    
    private fun drawCustom(canvas: Canvas) {
        // Custom drawing logic can be implemented here
        drawDynamicCross(canvas)
    }
    
    private fun drawCrossLines(canvas: Canvas, paint: Paint, length: Float, gapSize: Float) {
        // Horizontal lines
        canvas.drawLine(-length, 0f, -gapSize, 0f, paint)
        canvas.drawLine(gapSize, 0f, length, 0f, paint)
        
        // Vertical lines
        canvas.drawLine(0f, -length, 0f, -gapSize, paint)
        canvas.drawLine(0f, gapSize, 0f, length, paint)
    }
    
    private fun drawHitMarker(canvas: Canvas) {
        val markerPaint = Paint(crosshairPaint).apply {
            color = activeColor
            strokeWidth = thickness * 1.5f
            alpha = (255 * (1f - animationProgress)).toInt()
        }
        
        val markerSize = size * (1f + animationProgress * 0.5f)
        val angle = 45f
        
        canvas.save()
        canvas.rotate(angle)
        
        // Draw expanding X
        canvas.drawLine(-markerSize/2, -markerSize/2, markerSize/2, markerSize/2, markerPaint)
        canvas.drawLine(-markerSize/2, markerSize/2, markerSize/2, -markerSize/2, markerPaint)
        
        canvas.restore()
    }
    
    private fun updateAnimation(currentTime: Long) {
        when (currentFeedback) {
            FeedbackType.NONE -> {
                animationProgress = 0f
                pulseScale = 1f
                rotationAngle = 0f
                currentColor = if (_isActive.value) activeColor else baseColor
            }
            
            FeedbackType.PULSE -> {
                val elapsed = currentTime - animationStartTime
                animationProgress = (elapsed % PULSE_DURATION) / PULSE_DURATION.toFloat()
                pulseScale = 1f + 0.1f * sin(animationProgress * 2 * PI).toFloat()
                currentColor = if (_isActive.value) activeColor else baseColor
            }
            
            FeedbackType.SCALE -> {
                val elapsed = currentTime - animationStartTime
                if (elapsed < ANIMATION_DURATION) {
                    animationProgress = elapsed / ANIMATION_DURATION.toFloat()
                    pulseScale = 1f + 0.3f * (1f - animationProgress)
                } else {
                    pulseScale = 1f
                    currentFeedback = FeedbackType.NONE
                }
            }
            
            FeedbackType.COLOR_CHANGE -> {
                val elapsed = currentTime - animationStartTime
                if (elapsed < ANIMATION_DURATION) {
                    animationProgress = elapsed / ANIMATION_DURATION.toFloat()
                    currentColor = interpolateColor(errorColor, baseColor, animationProgress)
                } else {
                    currentColor = baseColor
                    currentFeedback = FeedbackType.NONE
                }
            }
            
            FeedbackType.ROTATION -> {
                val elapsed = currentTime - animationStartTime
                animationProgress = (elapsed % 2000) / 2000f
                rotationAngle = animationProgress * 360f
            }
            
            FeedbackType.HIT_MARKER -> {
                val elapsed = currentTime - animationStartTime
                if (elapsed < ANIMATION_DURATION) {
                    animationProgress = elapsed / ANIMATION_DURATION.toFloat()
                } else {
                    currentFeedback = FeedbackType.NONE
                }
            }
        }
    }
    
    /**
     * Trigger feedback animation
     */
    fun triggerFeedback(type: FeedbackType, startTime: Long = System.currentTimeMillis()) {
        currentFeedback = type
        animationStartTime = startTime
        animationProgress = 0f
        
        Log.d(TAG, "Triggered feedback: $type")
    }
    
    /**
     * Set crosshair style
     */
    fun setStyle(newStyle: CrosshairStyle) {
        style = newStyle
        Log.d(TAG, "Crosshair style changed to: $style")
    }
    
    /**
     * Configure crosshair appearance
     */
    fun configure(
        newSize: Float = size,
        newThickness: Float = thickness,
        newGap: Float = gap,
        newBaseColor: Int = baseColor,
        newActiveColor: Int = activeColor
    ) {
        size = newSize
        thickness = newThickness
        gap = newGap
        baseColor = newBaseColor
        activeColor = newActiveColor
        currentColor = baseColor
    }
    
    /**
     * Set visibility
     */
    fun setVisible(visible: Boolean) {
        _isVisible.value = visible
    }
    
    /**
     * Set active state
     */
    fun setActive(active: Boolean) {
        _isActive.value = active
        currentColor = if (active) activeColor else baseColor
    }
    
    /**
     * Utility function to adjust alpha of a color
     */
    private fun adjustAlpha(color: Int, alpha: Int): Int {
        return Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))
    }
    
    /**
     * Interpolate between two colors
     */
    private fun interpolateColor(startColor: Int, endColor: Int, fraction: Float): Int {
        val startA = Color.alpha(startColor)
        val startR = Color.red(startColor)
        val startG = Color.green(startColor)
        val startB = Color.blue(startColor)
        
        val endA = Color.alpha(endColor)
        val endR = Color.red(endColor)
        val endG = Color.green(endColor)
        val endB = Color.blue(endColor)
        
        return Color.argb(
            (startA + (endA - startA) * fraction).toInt(),
            (startR + (endR - startR) * fraction).toInt(),
            (startG + (endG - startG) * fraction).toInt(),
            (startB + (endB - startB) * fraction).toInt()
        )
    }
}