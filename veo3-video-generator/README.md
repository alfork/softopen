# Veo 3 Video Generator

A Python script for generating AI videos using Google's Veo 3 model with your own images or video clips. Uses the official Vertex AI REST API for direct integration.

## Features

✅ **Command-line Interface** - Easy to use with comprehensive argument parsing
✅ **Official Vertex AI REST API** - Uses Google's official REST API endpoints
✅ **Multiple Image Formats** - Support for PNG and JPEG images (local files or GCS)
✅ **Configurable Options** - Aspect ratio (16:9, 9:16), duration, seed, etc.
✅ **Auto MIME Type Detection** - Automatically detects image format
✅ **Progress Monitoring** - Real-time status updates during generation
✅ **Error Handling** - Comprehensive validation and error messages
✅ **Batch Processing** - Generate multiple videos from JSON configuration

## Prerequisites

- Google Cloud account with Vertex AI API enabled
- Python 3.7+ with `requests` library
- Google Cloud CLI (`gcloud`) installed and authenticated
- Images accessible as local files or uploaded to Google Cloud Storage
- Proper authentication configured

## Setup

### 1. Install Google Cloud CLI

Install the Google Cloud CLI if not already installed:

```bash
# On Linux/macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Or use package manager
# Ubuntu/Debian: sudo apt-get install google-cloud-cli
# macOS: brew install google-cloud-sdk
```

### 2. Authenticate with Google Cloud

```bash
# Login to your Google Cloud account
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Images

You can use either local image files or images stored in Google Cloud Storage:

**Option A: Local Images (Recommended)**
- Place your images in a local directory
- The script will automatically encode them for the API

**Option B: Google Cloud Storage**
```bash
# Create a bucket (if you don't have one)
gsutil mb gs://your-bucket-name

# Upload your images
gsutil cp /local/path/to/your-image.png gs://your-bucket-name/
```

## Usage

### Basic Usage with Local Image

```bash
python veo3_video_generator.py \
  --prompt "A sunrise over a mountain range" \
  --image-uri "/path/to/your/local-image.png" \
  --output-uri "gs://your-bucket/output-folder/"
```

### Basic Usage with GCS Image

```bash
python veo3_video_generator.py \
  --prompt "A sunrise over a mountain range" \
  --image-uri "gs://your-bucket/your-image.png" \
  --output-uri "gs://your-bucket/output-folder/"
```

### Advanced Usage

```bash
python veo3_video_generator.py \
  --prompt "Ocean waves crashing on the shore" \
  --image-uri "/path/to/ocean.jpg" \
  --output-uri "gs://your-bucket/videos/" \
  --aspect-ratio "9:16" \
  --duration 8 \
  --seed 12345
```

### Text-to-Video (No Image)

```bash
python veo3_video_generator.py \
  --prompt "A cat walking through a neon-lit city at night" \
  --duration 5
```

## Command Line Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--prompt` | Yes | Text description for video generation | `"A sunrise over mountains"` |
| `--image-uri` | Yes | GCS URI of input image | `"gs://bucket/image.png"` |
| `--output-uri` | Yes | GCS URI for output video | `"gs://bucket/output/"` |
| `--aspect-ratio` | No | Video aspect ratio (16:9 or 9:16) | `"16:9"` (default) |
| `--mime-type` | No | Image MIME type (auto-detected) | `"image/png"` |
| `--duration` | No | Video duration in seconds | `10` |
| `--seed` | No | Random seed for reproducible results | `12345` |

## Examples

### Generate a landscape video from a PNG image
```bash
python veo3_video_generator.py \
  --prompt "Time-lapse of clouds moving over a cityscape" \
  --image-uri "gs://my-bucket/cityscape.png" \
  --output-uri "gs://my-bucket/videos/"
```

### Generate a portrait video for social media
```bash
python veo3_video_generator.py \
  --prompt "A person walking through a busy street" \
  --image-uri "gs://my-bucket/street-photo.jpg" \
  --output-uri "gs://my-bucket/social-videos/" \
  --aspect-ratio "9:16"
```

### Generate with specific duration and seed
```bash
python veo3_video_generator.py \
  --prompt "Gentle rain falling on leaves" \
  --image-uri "gs://my-bucket/leaves.png" \
  --output-uri "gs://my-bucket/nature-videos/" \
  --duration 15 \
  --seed 42
```

## Supported Image Formats

- **PNG** (`.png`) - `image/png`
- **JPEG** (`.jpg`, `.jpeg`) - `image/jpeg`

**Recommended image resolution:** 1280x720 or higher for best results.

## Important Notes

- **Single Image per Request:** Veo 3 currently supports single-image-to-video generation per request
- **Multiple Clips:** For multiple clips or advanced editing, generate each scene separately and combine them afterward using video editing software
- **Google Drive Files:** If you want to use files from Google Drive, first transfer them to Google Cloud Storage
- **Processing Time:** Video generation can take several minutes depending on complexity and duration
- **Costs:** Be aware that using Veo 3 API incurs costs based on usage

## Troubleshooting

### Authentication Issues
```
❌ Failed to initialize Veo 3 client: ...
```
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Verify your service account has the necessary permissions
- Check that Vertex AI API is enabled in your Google Cloud project

### Invalid GCS URI
```
❌ Invalid GCS URI: ... Must start with 'gs://'
```
- Make sure your URIs start with `gs://`
- Example: `gs://my-bucket/my-image.png`

### Unsupported Image Format
```
❌ Unsupported image format. Use PNG or JPEG.
```
- Convert your images to PNG or JPEG format
- Supported extensions: `.png`, `.jpg`, `.jpeg`

## Output

The script will:
1. Validate your inputs
2. Start the video generation process
3. Monitor progress with status updates
4. Return the GCS URI of the generated video upon completion

Example output:
```
✅ Successfully initialized Veo 3 client
🔍 Auto-detected MIME type: image/png
🎬 Starting video generation...
   Prompt: A sunrise over mountains
   Input image: gs://my-bucket/sunrise.png
   Output location: gs://my-bucket/videos/
   Aspect ratio: 16:9
⏳ Video generation started. Waiting for completion...
   Still processing... (checking again in 15 seconds)
✅ Video generation completed successfully!
📹 Generated video GCS URI: gs://my-bucket/videos/generated_video_123.mp4

🎉 Success! Your video is ready at: gs://my-bucket/videos/generated_video_123.mp4
```

## License

This script is provided as-is for educational and development purposes. Please ensure you comply with Google Cloud's terms of service and Veo 3's usage policies.
