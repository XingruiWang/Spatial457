<div align="center">
  <img src="https://xingruiwang.github.io/projects/Spatial457/static/images/icon_name.png" alt="Spatial457 Logo" width="240"/>
</div>


<h1 align="center">
  <a href="https://arxiv.org/abs/2502.08636">
    Spatial457: A Diagnostic Benchmark for 6D Spatial Reasoning of Large Multimodal Models
  </a>
</h1>

<h4 align="center">
  <a href=".">Xingrui Wang</a><sup>1</sup>,
  <a href=".">Wufei Ma</a><sup>1</sup>,
  <a href=".">Tiezheng Zhang</a><sup>1</sup>,
  <a href=".">Celso M de Melo</a><sup>2</sup>,
  <a href=".">Jieneng Chen†</a><sup>1</sup>,
  <a href=".">Alan Yuille†</a><sup>1</sup>
</h4>

<p align="center">
  <sup>1</sup>Johns Hopkins University &nbsp;&nbsp;
  <sup>2</sup>DEVCOM Army Research Laboratory <br>
</p>

<p align="center">
  <a href="https://xingruiwang.github.io/projects/Spatial457/">Project Page</a> /
  <a href="https://arxiv.org/abs/2502.08636">Paper</a> /
  <a href="https://huggingface.co/datasets/RyanWW/Spatial457">Huggingface Data Card 🤗</a> /
  <a href="https://github.com/XingruiWang/Spatial457">Code</a>
</p>

<div align="center">
  <img src="./imgs/teaser.png" alt="Spatial457 Teaser" width="80%">
</div>

<p align="center"><i>
  Official implementation of the CVPR 2025 (Highlight) paper:<br>
  <strong>Spatial457: A Diagnostic Benchmark for 6D Spatial Reasoning of Large Multimodal Models</strong>
</i></p>


<h2 class="title is-3">🧠 Introduction</h2>
<p>
Spatial457 is a diagnostic benchmark designed to evaluate the 6D spatial reasoning capabilities of large multimodal models (LMMs). It systematically introduces four key capabilities—multi-object understanding, 2D and 3D localization, and 3D orientation—across five difficulty levels and seven question types, progressing from basic recognition to complex physical interaction.
</p>

<h2 class="title is-3">🚀 Quick Start</h2>

### For Evaluation Only

If you just want to evaluate models on Spatial457:

```bash
# Install VLMEvalKit
git clone https://github.com/open-compass/VLMEvalKit
cd VLMEvalKit
pip install -e .

# Run evaluation
python run.py --data Spatial457 --model <model_name>
```

The dataset (images + questions) will be automatically downloaded from [Hugging Face](https://huggingface.co/datasets/RyanWW/Spatial457).

### For Custom Dataset Generation

If you want to generate your own images and questions:

```bash
# 1. Clone this repository
git clone https://github.com/XingruiWang/Spatial457.git
cd Spatial457

# 2. Download 3D models and assets (required!)
cd image_generation
git clone https://huggingface.co/datasets/RyanWW/spatial457_meta_data
cp spatial457_meta_data/image_generation/data.zip .
unzip data.zip
cd ..

# 3. Install dependencies
pip install bpy==3.5.0
pip install -r requirement.txt

# 4. Generate images
bash scripts/render_images_realistic.sh

# 5. Generate questions
bash scripts/generate_questions.sh
```

<h2 class="title is-3">📦 Download</h2>

### Evaluation Dataset
<p>
You can access the full evaluation dataset and toolkit:
<ul>
  <li><strong>Dataset (Questions & Images):</strong> <a href="https://huggingface.co/datasets/RyanWW/Spatial457" target="_blank">Hugging Face - Spatial457</a></li>
  <li><strong>Code:</strong> <a href="https://github.com/XingruiWang/Spatial457" target="_blank">GitHub Repository</a></li>
  <li><strong>Paper:</strong> <a href="https://arxiv.org/abs/2502.08636" target="_blank">arXiv 2502.08636</a></li>
</ul>
</p>

### Generation Assets (Required for Custom Dataset Generation)
<p>
If you want to generate your own images and questions, download the 3D models and assets:
<ul>
  <li><strong>3D Models & Assets (data.zip):</strong> <a href="https://huggingface.co/datasets/RyanWW/spatial457_meta_data" target="_blank">Hugging Face - spatial457_meta_data</a></li>
  <li><strong>Size:</strong> ~2GB compressed, ~2.1GB uncompressed</li>
  <li><strong>Contents:</strong> CGPart 3D models, colored variants, textures, HDRI maps, Blender scenes</li>
</ul>
</p>

<p>
<strong>Quick download:</strong>
</p>

```bash
# Download 3D models and assets
cd image_generation
git clone https://huggingface.co/datasets/RyanWW/spatial457_meta_data
cp spatial457_meta_data/image_generation/data.zip .
unzip data.zip
```

<!--
<h2 class="title is-3">📊 Benchmark</h2>
<p>
We benchmarked a wide range of state-of-the-art models—including GPT-4o, Gemini, Claude, and several open-source LMMs—on all subsets. Performance consistently drops as task difficulty increases. PO3D-VQA and humans remain most robust across all levels.
</p>
<p>
The table below summarizes model performance across 7 subsets:
</p>
-->

# 🔥Run benchmark with [VLMEvalKit](https://github.com/open-compass/VLMEvalKit).

Spatial457 is also support by [VLMEvalKit](https://github.com/open-compass/VLMEvalKit)! Please try [here](https://github.com/open-compass/VLMEvalKit) for quick evaluation on most of the VLM. Evaluation can be done be running `run.py` in VLMEvalKit:

```
python run.py --data Spatial457 --model <model_name>
```

# 🛠️ Dataset Generation

We use Blender to render the scenes, so you can also add customized objects into the dataset. We also support customizing your own question types/templates for your studies.

## 📥 Prerequisites: Download Required Data

Before generating images or questions, you need to download the required 3D models and assets:

### Download `data.zip`

Download the data package from Hugging Face:

```bash
# Option 1: Using git clone (recommended)
cd image_generation
git clone https://huggingface.co/datasets/RyanWW/spatial457_meta_data
cp spatial457_meta_data/image_generation/data.zip .
unzip data.zip

# Option 2: Direct download
wget https://huggingface.co/datasets/RyanWW/spatial457_meta_data/resolve/main/image_generation/data.zip
unzip data.zip
```

### What's in `data.zip`?

The `data.zip` file (~2GB compressed, ~2.1GB uncompressed) contains **2,188 files** including:

```
data/
├── CGParts_colored/          # Colored 3D object models
│   ├── aeroplane/           # Aircraft models (various types)
│   ├── bicycle/             # Bicycle models
│   ├── bus/                 # Bus models (school, double, articulated)
│   ├── car/                 # Car models (various types)
│   └── motorbike/           # Motorbike models
├── CGPart/                   # Original CGPart dataset
│   ├── models/              # Base 3D models
│   ├── labels/              # Part annotations
│   ├── keypoints/           # Keypoint annotations
│   └── partobjs/            # Part-level objects
├── base_scene2.blend        # Base Blender scene file
├── HDRI_haven.json          # HDRI environment maps
├── colors.json              # Color definitions
├── properties_cgpart.json   # Object properties
└── save_models_1/           # Additional model data
    └── part_dict.json       # Part dictionary
```

Each object category contains:
- **models/**: Normalized 3D models (.obj, .mtl, .binvox, .json)
- **Colored variants**: 8 color versions (red, blue, yellow, green, cyan, purple, brown, gray)
- **images/**: Texture files for realistic rendering

## 🎨 Generate Images

After downloading and extracting `data.zip`, you can generate images:

### Installation

See `image_generation/README.md` for detailed setup instructions.

```bash
pip install bpy==3.5.0
pip install -r requirement.txt
```

### Run Image Generation

```bash
bash scripts/render_images_realistic.sh
```

**Note (Reproducing scenes):** If you want to reproduce scenes from pre-generated data (i.e., using `--load_scene 1`), download `spatial457_scenes_21k.json` from the [Hugging Face dataset](https://huggingface.co/datasets/RyanWW/Spatial457), then set `--clevr_scene_path` in `scripts/render_images_realistic.sh` (lines 22–23) to the downloaded path:

```bash
# Download: huggingface-cli download RyanWW/Spatial457 spatial457_scenes_21k.json --repo-type dataset --local-dir output/
# In render_images_realistic.sh, ensure: --clevr_scene_path $SPATIAL457_DIR/output/spatial457_scenes_21k.json
```

This will generate:
- **Images**: Rendered RGB images in `output/ver_realistic/images/`
- **Scene annotations**: JSON files with 3D scene information in `output/ver_realistic/scenes/`
- **Scene metadata**: Combined scene file `output/ver_realistic/superCLEVR_scenes.json`

## ❓ Generate Questions

After generating images and scene annotations, generate VQA questions:

### Run Question Generation

Set `input_scene_file` to your scene annotation JSON file:

```bash
bash scripts/generate_questions.sh
```

This script will generate questions for all difficulty levels (L1-L5) and question types:
- **L1**: Single object identification
- **L2**: Multi-object understanding
- **L3**: 2D spatial reasoning
- **L4**: Object occlusion and 3D pose
- **L5**: 6D spatial reasoning and collision detection

### Output

Generated questions will be saved in JSON format with the following structure:
```json
{
  "image_filename": "superCLEVR_new_000001.png",
  "question": "Is the large red object in front of the yellow car?",
  "answer": "True",
  "program": [...],
  "question_index": 100001
}
```


<h2 class="title is-3">Citation</h2>

```
@inproceedings{wang2025spatial457,
  title     = {Spatial457: A Diagnostic Benchmark for 6D Spatial Reasoning of Large Multimodal Models},
  author    = {Wang, Xingrui and Ma, Wufei and Zhang, Tiezheng and de Melo, Celso M and Chen, Jieneng and Yuille, Alan},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2025},
  url       = {https://arxiv.org/abs/2502.08636}
}
```

---




Content and toolkit are actively being updated. Stay tuned!
