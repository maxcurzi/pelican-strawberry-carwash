#!/usr/bin/env bash
# Render all frames headless on the GPU (Vulkan), then encode an MP4.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p frames
find frames -name '*.png' -delete
blender -b pelican_bicycle.blend --gpu-backend vulkan -o //frames/f_#### -F PNG -a > frames/render.log 2>&1
ffmpeg -y -loglevel error -framerate 24 -i frames/f_%04d.png -c:v libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p -movflags +faststart pelican_strawberry_carwash.mp4
echo "frames: $(find frames -name '*.png' | wc -l)"
