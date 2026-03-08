
# Image Generation

## Setup

Install the required Blender version:

```bash
pip install bpy==3.5.0
```

Then install [Kubric](https://github.com/google-research/kubric), which is required for accessing HDRi assets. Note that PyBullet is not required for this task.

Install all dependencies from the requirements file:

```bash
pip install -r requirements.txt
```

## Run

To generate realistic images, execute the following script:

```bash
bash scripts/render_images_realistic.sh
```
