
cd image_generation

python super_restore_render_images_realistic_texture.py -- \
    --start_idx 0 \
    --num_images 25000 \
    --use_gpu 1 \
    --shape_dir data/CGPart \
    --model_dir data/CGParts_colored \
    --properties_json data/properties_cgpart.json \
    --margin 0.1 \
    --save_blendfiles 0 \
    --width 640 \
    --height 480 \
    --output_image_dir ../output/ver_realistic/images/ \
    --output_scene_dir ../output/ver_realistic/scenes/ \
    --output_blend_dir ../output/ver_realistic/blendfiles \
    --output_scene_file ../output/ver_realistic/superCLEVR_scenes.json \
    --is_part 0 \
    --load_scene 1 \

    # --load_scene 1 \
    # --clevr_scene_path /mnt/ccvl15/xingrui/superclevr_6d/superCLEVR_scenes.json
    # --clevr_scene_path ../output/ver_mask_teaser/superCLEVR_scenes.json 

cd ..

