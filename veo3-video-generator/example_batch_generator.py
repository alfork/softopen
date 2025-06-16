#!/usr/bin/env python3
"""
Batch Veo 3 Video Generator

This script demonstrates how to generate multiple videos from a list of images and prompts.
Useful for creating multiple video clips that can be combined later.

Usage:
    python example_batch_generator.py --config batch_config.json
"""

import json
import argparse
import sys
from pathlib import Path
from veo3_video_generator import Veo3VideoGenerator


def load_batch_config(config_file):
    """Load batch configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Error loading config file: {e}")
        sys.exit(1)


def validate_batch_config(config):
    """Validate the batch configuration structure"""
    required_keys = ['videos', 'default_settings']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key in config: {key}")
    
    if not isinstance(config['videos'], list):
        raise ValueError("'videos' must be a list")
    
    for i, video in enumerate(config['videos']):
        required_video_keys = ['prompt', 'image_uri']
        for key in required_video_keys:
            if key not in video:
                raise ValueError(f"Video {i}: Missing required key '{key}'")


def generate_batch_videos(config_file):
    """Generate multiple videos based on configuration file"""
    print("🎬 Starting batch video generation...")
    
    config = load_batch_config(config_file)
    validate_batch_config(config)
    
    generator = Veo3VideoGenerator()
    
    defaults = config['default_settings']
    
    results = []
    total_videos = len(config['videos'])
    
    for i, video_config in enumerate(config['videos'], 1):
        print(f"\n📹 Processing video {i}/{total_videos}")
        print(f"   Prompt: {video_config['prompt']}")
        
        settings = {**defaults, **video_config}
        
        try:
            if 'mime_type' not in settings:
                settings['mime_type'] = generator.detect_mime_type(settings['image_uri'])
            
            result_uri = generator.generate_video(
                prompt=settings['prompt'],
                image_uri=settings['image_uri'],
                image_mime_type=settings['mime_type'],
                output_gcs_uri=settings['output_gcs_uri'],
                aspect_ratio=settings.get('aspect_ratio', '16:9'),
                duration=settings.get('duration'),
                seed=settings.get('seed')
            )
            
            if result_uri:
                results.append({
                    'index': i,
                    'prompt': settings['prompt'],
                    'image_uri': settings['image_uri'],
                    'video_uri': result_uri,
                    'status': 'success'
                })
                print(f"✅ Video {i} completed: {result_uri}")
            else:
                results.append({
                    'index': i,
                    'prompt': settings['prompt'],
                    'image_uri': settings['image_uri'],
                    'video_uri': None,
                    'status': 'failed'
                })
                print(f"❌ Video {i} failed")
                
        except Exception as e:
            print(f"❌ Error processing video {i}: {e}")
            results.append({
                'index': i,
                'prompt': settings['prompt'],
                'image_uri': settings['image_uri'],
                'video_uri': None,
                'status': 'error',
                'error': str(e)
            })
    
    print(f"\n📊 Batch Generation Summary")
    print(f"   Total videos: {total_videos}")
    successful = len([r for r in results if r['status'] == 'success'])
    failed = total_videos - successful
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    
    results_file = 'batch_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   Results saved to: {results_file}")
    
    return results


def create_example_config():
    """Create an example batch configuration file"""
    example_config = {
        "default_settings": {
            "output_gcs_uri": "gs://your-bucket/batch-videos/",
            "aspect_ratio": "16:9"
        },
        "videos": [
            {
                "prompt": "A sunrise over a mountain range with golden light",
                "image_uri": "gs://your-bucket/mountain-sunrise.png"
            },
            {
                "prompt": "Ocean waves gently lapping on a sandy beach",
                "image_uri": "gs://your-bucket/beach-scene.jpg",
                "aspect_ratio": "9:16"
            },
            {
                "prompt": "City traffic moving through busy streets at dusk",
                "image_uri": "gs://your-bucket/city-traffic.png",
                "duration": 8
            },
            {
                "prompt": "Leaves rustling in the wind on a sunny day",
                "image_uri": "gs://your-bucket/forest-leaves.jpg",
                "seed": 42
            }
        ]
    }
    
    config_file = 'example_batch_config.json'
    with open(config_file, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"📝 Example configuration created: {config_file}")
    print("Edit this file with your actual GCS URIs and prompts, then run:")
    print(f"python example_batch_generator.py --config {config_file}")


def main():
    """Main function for batch video generation"""
    parser = argparse.ArgumentParser(
        description="Generate multiple videos using Veo 3 in batch mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example configuration file structure:
{
  "default_settings": {
    "output_gcs_uri": "gs://your-bucket/videos/",
    "aspect_ratio": "16:9"
  },
  "videos": [
    {
      "prompt": "A sunrise over mountains",
      "image_uri": "gs://your-bucket/sunrise.png"
    },
    {
      "prompt": "Ocean waves",
      "image_uri": "gs://your-bucket/ocean.jpg",
      "aspect_ratio": "9:16"
    }
  ]
}
        """
    )
    
    parser.add_argument(
        "--config",
        help="Path to JSON configuration file"
    )
    
    parser.add_argument(
        "--create-example",
        action="store_true",
        help="Create an example configuration file"
    )
    
    args = parser.parse_args()
    
    if args.create_example:
        create_example_config()
        return
    
    if not args.config:
        print("❌ Error: --config is required (or use --create-example)")
        parser.print_help()
        sys.exit(1)
    
    if not Path(args.config).exists():
        print(f"❌ Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        results = generate_batch_videos(args.config)
        
        failed_count = len([r for r in results if r['status'] != 'success'])
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} videos failed to generate")
            sys.exit(1)
        else:
            print(f"\n🎉 All videos generated successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Batch generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
