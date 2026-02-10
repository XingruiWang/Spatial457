
# Image Generation

This directory contains code for generating realistic 3D rendered images using Blender.

## 📥 Step 1: Download Required Data

**IMPORTANT**: Before running any code, you must download the `data.zip` file containing 3D models and assets.

### Download from Hugging Face

```bash
# Option 1: Using git clone (recommended)
git clone https://huggingface.co/datasets/RyanWW/spatial457_meta_data
cp spatial457_meta_data/image_generation/data.zip .
unzip data.zip

# Option 2: Direct download using wget
wget https://huggingface.co/datasets/RyanWW/spatial457_meta_data/resolve/main/image_generation/data.zip
unzip data.zip

# Option 3: Direct download using curl
curl -L -o data.zip https://huggingface.co/datasets/RyanWW/spatial457_meta_data/resolve/main/image_generation/data.zip
unzip data.zip
```

### Verify Download

After extraction, you should have a `data/` directory with the following structure:

```
image_generation/
├── data/
│   ├── CGParts_colored/      # Colored 3D models (aeroplane, bicycle, bus, car, motorbike)
│   ├── CGPart/               # Original CGPart dataset
│   ├── base_scene2.blend     # Base Blender scene
│   ├── HDRI_haven.json       # HDRI environment maps
│   ├── colors.json           # Color definitions
│   ├── properties_cgpart.json # Object properties
│   └── save_models_1/        # Additional model data
├── super_restore_render_images_realistic_texture.py
├── utils.py
└── ...
```

**File size**: ~2GB compressed, ~2.1GB uncompressed, 2,188 files

## 🔧 Step 2: Setup Environment

### Install Blender Python API

Install the required Blender version:

```bash
pip install bpy==3.5.0
```

### Install Kubric

Install [Kubric](https://github.com/google-research/kubric), which is required for accessing HDRi assets. Note that PyBullet is not required for this task.

```bash
git clone https://github.com/google-research/kubric.git
cd kubric
pip install -e .
cd ..
```

### Install Other Dependencies

Install all dependencies from the requirements file:

```bash
pip install -r ../requirement.txt
```

## 🚀 Step 3: Run Image Generation

To generate realistic images, execute the following script from the project root:

```bash
bash scripts/render_images_realistic.sh
```

### What This Script Does

The script will:
1. Load 3D models from `data/CGParts_colored/`
2. Randomly place objects in a 3D scene
3. Apply realistic textures and lighting (using HDRI)
4. Render images at 640×480 resolution
5. Save outputs to `output/ver_realistic/`:
   - `images/`: Rendered PNG images
   - `scenes/`: Per-image scene annotations (JSON)
   - `superCLEVR_scenes.json`: Combined scene metadata

### Configuration

You can modify parameters in `scripts/render_images_realistic.sh`:

```bash
--start_idx 0              # Starting image index
--num_images 25000         # Number of images to generate
--width 640                # Image width
--height 480               # Image height
--use_gpu 1                # Use GPU for rendering (1=yes, 0=no)
--shape_dir data/CGPart    # Path to shape data
--model_dir data/CGParts_colored  # Path to colored models
```

## 📊 Output Format

### Generated Images
- Format: PNG
- Resolution: 640×480 pixels
- Naming: `superCLEVR_new_XXXXXX.png`

### Scene Annotations (JSON)
Each scene JSON contains:
```json
{
  "image_filename": "superCLEVR_new_000001.png",
  "objects": [
    {
      "shape": "car",
      "color": "red",
      "size": "large",
      "position": [x, y, z],
      "rotation": [rx, ry, rz],
      "3d_coords": [...],
      ...
    }
  ],
  "relationships": {...}
}
```

## 🛠️ Troubleshooting

### Error: "data/ directory not found"
Make sure you've downloaded and extracted `data.zip` in the `image_generation/` directory.

### Error: "bpy module not found"
Install Blender Python API: `pip install bpy==3.5.0`

### Slow rendering
Enable GPU rendering by setting `--use_gpu 1` in the script.
