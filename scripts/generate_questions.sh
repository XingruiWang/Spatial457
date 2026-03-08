cd question_generation
START_IDX=0


# L1 L0_object_identification_easy
python generate_questions_pose.py\
   --input_scene_file /home/xingrui/publish/3D-Aware-VQA/superclevr-3D-question/output/ver_mask_30k_clean/superCLEVR_scenes_30k_occlusion.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 2 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L1/sulerclevr_questions_object.json \
   --template_dir TEMPLATES/L0_object_identification \


# L1 L0_object_identification
python generate_questions_pose.py\
   --input_scene_file /home/xingrui/publish/3D-Aware-VQA/superclevr-3D-question/output/ver_mask_30k_clean/superCLEVR_scenes_30k_occlusion.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L1/sulerclevr_questions_object.json \
   --template_dir TEMPLATES/L0_object_identification \





# L1 spatial
python generate_questions_pose.py\
   --input_scene_file /home/xingrui/publish/3D-Aware-VQA/superclevr-3D-question/output/ver_mask_30k_clean/superCLEVR_scenes_30k_occlusion.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L1/sulerclevr_questions_2D_spatial_aux.json \
   --template_dir TEMPLATES/L1_L3_spatial_questions \



#L4 occ
python generate_questions_pose.py \
   --input_scene_file /home/xingrui/publish/3D-Aware-VQA/superclevr-3D-question/output/ver_mask_30k_clean/superCLEVR_scenes_30k_occlusion.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L2/superclevr_questions_obj_occ.json \
   --template_dir TEMPLATES/L2_object_occlusion/ \
   --remove_redundant 1.0


# L4 pose
python generate_questions_pose.py \
   --input_scene_file /home/xingrui/publish/3D-Aware-VQA/superclevr-3D-question/output/ver_mask_30k_clean/superCLEVR_scenes_30k_occlusion.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L2/superclevr_questions_pose.json \
   --template_dir TEMPLATES/L2_pose/ \
   --remove_redundant 1.0 \
   --contain_pose


# L5 questions

python generate_questions_pose.py \
   --input_scene_file ../output/ver_6d_questions/superCLEVR_scenes.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L3/superclevr_questions_6d.json \
   --template_dir TEMPLATES/L1_L3_spatial_questions \
# --remove_redundant 1.0


python generate_questions_physics.py \
   --input_scene_file ../output/ver_6d_questions/superCLEVR_scenes_with_collision.json \
   --scene_start_idx ${START_IDX} \
   --num_scenes 1000 \
   --instances_per_template 1 \
   --templates_per_image 5 \
   --metadata_file metadata_part_occlusion.json \
   --output_questions_file ../output/ver_6d_questions/questions/L3/superclevr_questions_physics.json \
   --template_dir TEMPLATES/L3_physics \
#    --remove_redundant 0.5