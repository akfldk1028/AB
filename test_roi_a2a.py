"""
Test ROI Processing for A2A System
Real test with specific ROI coordinates: {x:100, y:200, w:300, h:400}
"""

import asyncio
import sys
from pathlib import Path
import json
import numpy as np
from PIL import Image
import io

# Add module path
sys.path.append(str(Path(__file__).parent / 'a2a-module'))

from agents.claude_cli.vision.roi_processor import (
    ROIProcessor, 
    ROICoordinates, 
    ROIAnalysisMode,
    ROITracker
)
from agents.claude_cli.vision.android_xr_utils import (
    AndroidXRBridge,
    AndroidXRDataFormatter,
    XRSceneOptimizer,
    PerformanceMonitor
)


async def test_real_roi_processing():
    """Test ROI processing with real A2A coordinates"""
    
    print("=" * 60)
    print("A2A ROI Processing Test")
    print("ROI Coordinates: {x:100, y:200, w:300, h:400}")
    print("=" * 60)
    
    # Initialize components
    bridge = AndroidXRBridge()
    processor = ROIProcessor(bridge=bridge)
    optimizer = XRSceneOptimizer()
    monitor = PerformanceMonitor()
    
    # Your specific ROI coordinates
    roi = ROICoordinates(x=100, y=200, width=300, height=400)
    
    print(f"\n1. ROI Properties:")
    print(f"   - Position: ({roi.x}, {roi.y})")
    print(f"   - Size: {roi.width}x{roi.height}")
    print(f"   - Center: {roi.get_center()}")
    print(f"   - Area: {roi.get_area()} pixels")
    print(f"   - Bounds: {roi.get_bounds()}")
    
    # Create test image (1920x1080 HD resolution)
    print(f"\n2. Creating test image (1920x1080)...")
    test_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # Add some pattern to ROI area for visual distinction
    x1, y1, x2, y2 = roi.get_bounds()
    test_image[y1:y2, x1:x2] = [100, 150, 200]  # Blue-ish color
    
    # Validate ROI
    is_valid = processor.validate_roi(roi, (1920, 1080))
    print(f"   - ROI validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Process ROI with different AI analysis modes
    print(f"\n3. Processing ROI with AI Analysis Modes:")
    
    modes_to_test = [
        (ROIAnalysisMode.OBJECT_DETECTION, "Object Detection"),
        (ROIAnalysisMode.SCENE_UNDERSTANDING, "Scene Understanding"),
        (ROIAnalysisMode.TEXT_RECOGNITION, "Text Recognition"),
        (ROIAnalysisMode.GESTURE_RECOGNITION, "Gesture Recognition"),
        (ROIAnalysisMode.DEPTH_ESTIMATION, "Depth Estimation")
    ]
    
    all_results = []
    
    for mode, mode_name in modes_to_test:
        print(f"\n   {mode_name}:")
        
        # Start monitoring
        start_time = asyncio.get_event_loop().time()
        
        # Process ROI
        result = await processor.process_roi(
            test_image, 
            roi, 
            mode,
            options={'test_mode': True, 'a2a_enabled': True}
        )
        
        # Record performance
        processing_time = asyncio.get_event_loop().time() - start_time
        monitor.record_frame(processing_time, result.confidence)
        
        # Display results
        print(f"     - Confidence: {result.confidence:.2%}")
        print(f"     - Labels: {', '.join(result.labels[:3])}")
        print(f"     - Processing: {result.processing_time:.3f}s")
        
        if result.features:
            print(f"     - Features:")
            for key, value in list(result.features.items())[:3]:
                if isinstance(value, (int, float, str)):
                    print(f"         - {key}: {value}")
        
        all_results.append(result)
    
    # Test ROI expansion
    print(f"\n4. ROI Expansion Test:")
    expanded_roi = roi.expand(factor=1.5)
    print(f"   - Original: {roi.width}x{roi.height} at ({roi.x}, {roi.y})")
    print(f"   - Expanded: {expanded_roi.width}x{expanded_roi.height} at ({expanded_roi.x}, {expanded_roi.y})")
    
    # Test ROI optimization
    print(f"\n5. ROI Optimization for Performance:")
    optimized_roi = await processor.optimize_roi_for_performance(roi, target_size=(640, 480))
    print(f"   - Optimized size: {optimized_roi.width}x{optimized_roi.height}")
    
    # Test multiple ROI processing
    print(f"\n6. Multiple ROI Processing (Parallel):")
    multiple_rois = [
        roi,
        ROICoordinates(x=500, y=300, width=200, height=200),
        ROICoordinates(x=800, y=100, width=250, height=350)
    ]
    
    multi_results = await processor.process_multiple_rois(
        test_image,
        multiple_rois,
        ROIAnalysisMode.OBJECT_DETECTION,
        parallel=True
    )
    
    print(f"   - Processed {len(multi_results)} ROIs in parallel")
    for i, result in enumerate(multi_results):
        print(f"     - ROI {i+1}: {result.labels[0] if result.labels else 'unknown'} (conf: {result.confidence:.2%})")
    
    # Test ROI tracking
    print(f"\n7. ROI Tracking Across Frames:")
    tracker = ROITracker()
    
    for frame_num in range(3):
        # Simulate slight movement
        moved_roi = ROICoordinates(
            x=roi.x + frame_num * 10,
            y=roi.y + frame_num * 5,
            width=roi.width,
            height=roi.height
        )
        
        tracked = tracker.update([moved_roi])
        for track_id, tracked_roi in tracked:
            print(f"   - Frame {frame_num}: Track ID {track_id} at ({tracked_roi.x}, {tracked_roi.y})")
    
    # Convert to A2A format
    print(f"\n8. A2A Protocol Format:")
    a2a_message = all_results[0].to_a2a_format()
    print(json.dumps(a2a_message, indent=2))
    
    # Format for Android XR
    print(f"\n9. Android XR Integration:")
    
    # Convert to ARCore format
    arcore_data = AndroidXRDataFormatter.format_for_arcore([{
        'type': 'object',
        'track_id': 1,
        'position': [roi.get_center()[0], roi.get_center()[1], 0],
        'rotation': [0, 0, 0, 1],
        'confidence': 0.95
    }])
    print(f"   - ARCore format: {json.dumps(arcore_data, indent=2)[:200]}...")
    
    # Convert to Unity XR format
    unity_data = AndroidXRDataFormatter.format_for_unity_xr([{
        'label': 'ROI_Object',
        'position': [roi.get_center()[0], roi.get_center()[1], 0],
        'rotation': [0, 0, 0, 1],
        'scale': [1, 1, 1],
        'metadata': {'roi': roi.to_dict()}
    }])
    print(f"   - Unity XR format: {json.dumps(json.loads(unity_data), indent=2)[:200]}...")
    
    # Performance metrics
    print(f"\n10. Performance Metrics:")
    perf_metrics = monitor.get_metrics()
    print(f"    - FPS: {perf_metrics['fps']:.1f}")
    print(f"    - Avg Processing: {perf_metrics['avg_processing_time']:.3f}s")
    print(f"    - Avg Confidence: {perf_metrics['avg_confidence']:.2%}")
    
    proc_metrics = processor.get_metrics()
    print(f"    - Total Processed: {proc_metrics['total_processed']}")
    print(f"    - Average Time: {proc_metrics['average_time']:.3f}s")
    
    # Check cache efficiency
    print(f"\n11. Cache Efficiency Test:")
    print(f"    - Processing same ROI again (should use cache)...")
    
    cached_result = await processor.process_roi(
        test_image, 
        roi, 
        ROIAnalysisMode.OBJECT_DETECTION
    )
    print(f"    - Result retrieved (from cache if < 5s)")
    
    # Simulate sending to Android
    print(f"\n12. Simulating Android XR Communication:")
    bridge.send_to_android('roi_analysis', {
        'roi': roi.to_dict(),
        'analysis_modes': [mode.value for mode, _ in modes_to_test],
        'results_count': len(all_results),
        'timestamp': asyncio.get_event_loop().time()
    })
    print(f"    - Sent {len(bridge.message_queue)} messages to Android XR")
    
    # ROI importance calculation
    print(f"\n13. ROI Importance Scoring:")
    roi_metadata = {
        'contains_face': False,
        'contains_text': True,
        'motion_detected': True,
        'user_gaze': False,
        'size_ratio': roi.get_area() / (1920 * 1080)
    }
    
    importance = optimizer.calculate_roi_importance(roi_metadata)
    print(f"    - ROI Importance Score: {importance:.2f}")
    print(f"    - Should Analyze: {optimizer.should_analyze_region('roi_100_200', importance)}")
    
    print("\n" + "=" * 60)
    print("A2A ROI Processing Test Complete!")
    print("=" * 60)


async def test_roi_intersection():
    """Test ROI intersection and overlap detection"""
    
    print("\n" + "=" * 60)
    print("ROI Intersection Test")
    print("=" * 60)
    
    # Your specific ROI
    roi1 = ROICoordinates(x=100, y=200, width=300, height=400)
    
    # Test various overlapping scenarios
    test_cases = [
        (ROICoordinates(x=200, y=300, width=200, height=200), "Partial overlap"),
        (ROICoordinates(x=150, y=250, width=100, height=100), "Fully contained"),
        (ROICoordinates(x=500, y=700, width=100, height=100), "No overlap"),
        (ROICoordinates(x=50, y=150, width=400, height=500), "Contains original")
    ]
    
    for roi2, description in test_cases:
        print(f"\n{description}:")
        print(f"  ROI1: {roi1.to_dict()}")
        print(f"  ROI2: {roi2.to_dict()}")
        print(f"  Intersects: {roi1.intersects(roi2)}")
        
        intersection = roi1.intersection(roi2)
        if intersection:
            print(f"  Intersection: {intersection.to_dict()}")
            print(f"  Intersection area: {intersection.get_area()}")


if __name__ == "__main__":
    print("Starting A2A ROI Processing Test...")
    
    # Run main test
    asyncio.run(test_real_roi_processing())
    
    # Run intersection test
    asyncio.run(test_roi_intersection())