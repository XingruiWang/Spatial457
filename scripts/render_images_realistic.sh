
cd image_generation

SPATIAL457_DIR=/Path/to/Spatial457
python super_restore_render_images_realistic_texture.py -- \
    --start_idx 20000 \
    --num_images 100 \
    --use_gpu 1 \
    --shape_dir data/CGPart \
    --model_dir data/CGParts_colored \
    --properties_json data/properties_cgpart.json \
    --margin 0.1 \
    --save_blendfiles 1 \
    --width 640 \
    --height 480 \
    --output_image_dir $SPATIAL457_DIR/output/spatial457/images/ \
    --output_scene_dir $SPATIAL457_DIR/output/spatial457/scenes/ \
    --output_blend_dir $SPATIAL457_DIR/output/spatial457/blendfiles/ \
    --output_scene_file $SPATIAL457_DIR/output/spatial457/spatial457_scenes.json \
    --is_part 0 \
    --load_scene 1 \
    --clevr_scene_path $SPATIAL457_DIR/output/spatial457_scenes_21k.json\

    # --load_scene 1 \
    # --clevr_scene_path /mnt/ccvl15/xingrui/superclevr_6d/superCLEVR_scenes.json
    # --clevr_scene_path ../output/ver_mask_teaser/superCLEVR_scenes.json 

cd ..




